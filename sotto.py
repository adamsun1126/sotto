#!/usr/bin/env python3
"""
sotto - personal push-to-talk dictation, fully local, zero logging.

Hold a hotkey and speak -> release -> Whisper transcribes -> a local LLM cleans
up the wording -> the text is pasted at the cursor. Audio lives only in memory;
nothing is ever written to disk.
"""
import os
import sys
import json
import time
import ctypes
import shutil
import queue
import socket
import re
import threading
import subprocess
import urllib.request

import numpy as np
import sounddevice as sd
from pynput import keyboard

# ---------- settings (override with environment variables) ----------
HOTKEY      = os.environ.get("FLOW_HOTKEY", "right_option")   # key to hold while speaking
KEY_ALIASES = {  # friendly names -> pynput names
    "right_option": "alt_r", "left_option": "alt_l", "option": "alt_l",
    "right_cmd": "cmd_r", "left_cmd": "cmd_l", "right_ctrl": "ctrl_r", "left_ctrl": "ctrl_l",
    "right_shift": "shift_r", "left_shift": "shift_l", "fn": "fn", "caps_lock": "caps_lock",
}
WHISPER     = os.environ.get("FLOW_WHISPER", "mlx-community/whisper-large-v3-turbo")
LLM         = os.environ.get("FLOW_LLM", "qwen2.5:7b")         # Ollama model for cleanup
LANG        = os.environ.get("FLOW_LANG", None)                # force "zh" or "en"; None = auto
CLEANUP     = os.environ.get("FLOW_CLEANUP", "1") == "1"       # 0 = raw transcript only
LANGS       = ("en", "zh")                                     # supported languages
OLLAMA_URL  = "http://127.0.0.1:11434/api/chat"
SAMPLE_RATE = 16000
MIN_RMS     = 0.004     # below this the recording is treated as silence
MAX_CLEANUP_CHARS = 6000  # longer transcripts are pasted raw (LLM context / latency)
# Phrases Whisper hallucinates on silence or noise. Compared lowercase, punctuation stripped.
HALLUCINATIONS = {
    "thank you", "thanks for watching", "thank you for watching", "thanks for listening",
    "subscribe", "please subscribe", "like and subscribe", "see you next time", "bye", "you",
    "字幕由amara org社群提供", "字幕由amaraorg社群提供", "請不吝點贊訂閱轉發打賞支持明鏡與點點欄目",
    "謝謝觀看", "謝謝收看", "謝謝大家", "明鏡與點點欄目", "字幕製作", "訂閱",
}

PROMPTS = {
    "en": {
        "system": """You clean up raw English speech-to-text transcripts so they can be pasted as-is.
Rules:
- Remove fillers, stutters and repeated words (um, uh, like, you know, "the the").
- If the speaker corrects themselves ("no wait", "actually", "I mean"), keep only the corrected version and drop the mistake.
- Add proper punctuation (ASCII . , ? !) and paragraph breaks.
- Do not change the meaning, add or drop information, or answer the content.
- Write in English. Never translate. Keep any foreign words exactly as spoken.
- Output only the cleaned text: no explanations, no preamble, no quotes.""",
        "examples": [
            ("um so can you uh send the the report to to John by by tomorrow no wait by Friday",
             "Can you send the report to John by Friday?"),
            ("let's uh meet at three no actually four at the the cafe",
             "Let's meet at four at the cafe."),
        ],
    },
    "zh": {
        "system": """你負責整理中文（可夾雜英文）的語音逐字稿，讓它能直接貼上使用。
規則：
- 去掉口頭禪、贅字、重複、結巴（嗯、呃、就是、那個、然後然後）。
- 說話者若中途改口（「不對」、「不是」、「我是說」），只保留改口後的內容，刪掉說錯的部分。
- 補上正確的全形標點（。，？！）與分段。
- 不改變原意、不增減資訊、不回答內容。
- 一律輸出繁體中文，不可翻譯；原文中的英文單字保持英文原樣。
- 只輸出整理後的文字，不要任何說明、前言或引號。""",
        "examples": [
            ("嗯 那個 我想說明天 不對 後天下午三點 我們在 就是 台北車站碰面 然後然後再一起去 去看那個 demo",
             "後天下午三點我們在台北車站碰面，然後一起去看 demo。"),
            ("這個 請幫我 幫我把 report 寄給 寄給老闆 然後 嗯 副本給 Amy",
             "請幫我把 report 寄給老闆，副本給 Amy。"),
        ],
    },
}

def log(msg):
    print(msg, flush=True)

# ---------- recording ----------
class MicError(Exception):
    pass

class Recorder:
    """Records from the default input device at its native rate; returns 16 kHz mono float32."""
    def __init__(self):
        self.frames = []
        self.stream = None
        self.rate = SAMPLE_RATE
        self.lock = threading.Lock()

    def _open(self):
        dev = sd.query_devices(kind="input")
        self.rate = int(dev["default_samplerate"]) or SAMPLE_RATE
        stream = sd.InputStream(
            samplerate=self.rate, channels=1, dtype="float32",
            callback=lambda indata, *_: self.frames.append(indata.copy()))
        stream.start()
        return stream

    def start(self):
        with self.lock:
            if self.stream:
                return
            self.frames = []
            try:
                self.stream = self._open()
            except Exception:
                # Device list may be stale after headphones/mics were (un)plugged: reset PortAudio and retry once.
                try:
                    sd._terminate(); sd._initialize()
                    self.stream = self._open()
                except Exception as e:
                    raise MicError(e) from e

    def stop(self):
        with self.lock:
            if not self.stream:
                return None
            self.stream.stop(); self.stream.close(); self.stream = None
            if not self.frames:
                return None
            audio = np.concatenate(self.frames)[:, 0]
            if self.rate != SAMPLE_RATE:
                n = int(len(audio) * SAMPLE_RATE / self.rate)
                audio = np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio).astype(np.float32)
            return audio

def check_microphone():
    try:
        dev = sd.query_devices(kind="input")
        s = sd.InputStream(samplerate=int(dev["default_samplerate"]), channels=1, dtype="float32")
        s.start(); s.stop(); s.close()
        log(f"Microphone: {dev['name']}")
    except Exception as e:
        log(f"WARNING: cannot open the microphone ({e}).")
        log("Check System Settings > Privacy & Security > Microphone for the app running this script, and that no other app holds the mic.")
        subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"])

# ---------- transcribe + cleanup ----------
_cc = None
def to_traditional(text):
    global _cc
    if _cc is None:
        from opencc import OpenCC
        _cc = OpenCC("s2twp")
    return _cc.convert(text)

_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
_PUNCT = re.compile(r"[\s\.,!?;:'\"\-\u3000-\u303f\uff00-\uffef]+")

_HALLU_NORM = {_PUNCT.sub("", h.lower()) for h in HALLUCINATIONS}

def is_hallucination(text):
    norm = _PUNCT.sub("", text.lower())
    return norm == "" or norm in _HALLU_NORM

def transcribe(audio):
    """Returns (text, language). Empty text means nothing usable was heard."""
    import mlx_whisper
    if float(np.sqrt(np.mean(audio ** 2))) < MIN_RMS:
        return "", LANG or "en"
    out = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER, language=LANG, verbose=None)
    lang = out.get("language") or LANG
    if lang not in LANGS:
        # Misdetected (e.g. Chinese as Japanese/Cantonese, English as Dutch): pick by script and redo.
        lang = "zh" if _CJK.search(out["text"]) else "en"
        out = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER, language=lang, verbose=None)
    # Whisper's own rule: a segment is silence only if no-speech is likely AND the decode was low-confidence.
    segs = [sg for sg in out.get("segments", [])
            if not (sg.get("no_speech_prob", 0) > 0.6 and sg.get("avg_logprob", 0) < -1.0)]
    text = "".join(sg["text"] for sg in segs).strip() if out.get("segments") else out["text"].strip()
    if is_hallucination(text):
        return "", lang
    if lang == "zh":
        text = to_traditional(text)
    return text, lang

def _tokens(text, lang):
    t = _PUNCT.sub(" " if lang == "en" else "", text.lower())
    return set(t.split()) if lang == "en" else set(t)

def faithful(raw, cleaned, lang):
    """True if `cleaned` is plausibly a tidied copy of `raw` rather than new content.
    Guards against the LLM answering, obeying spoken 'instructions', or hallucinating."""
    if not cleaned or len(cleaned) > 1.5 * len(raw) + 40:
        return False
    a, b = _tokens(raw, lang), _tokens(cleaned, lang)
    if not b:
        return False
    return len(a & b) / len(b) >= 0.6   # most of the output must come from the input

OLLAMA_BASE = OLLAMA_URL.rsplit("/api/", 1)[0]
_ollama_proc = None

def ollama_alive():
    try:
        with urllib.request.urlopen(OLLAMA_BASE + "/api/tags", timeout=2) as r:
            return json.load(r)
    except Exception:
        return None

def ensure_ollama():
    """Start `ollama serve` if nothing answers, wait until it does, and check the model is pulled.
    Returns True when cleanup can be used."""
    global _ollama_proc
    tags = ollama_alive()
    if tags is None:
        exe = shutil.which("ollama") or "/opt/homebrew/bin/ollama"
        if not os.path.exists(exe):
            log("WARNING: Ollama is not installed (brew install ollama). Transcripts will be pasted without cleanup.")
            return False
        log("Starting Ollama...")
        _ollama_proc = subprocess.Popen([exe, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                        start_new_session=True)
        for _ in range(60):
            time.sleep(0.5)
            tags = ollama_alive()
            if tags is not None:
                break
        else:
            log("WARNING: Ollama did not start within 30 s. Transcripts will be pasted without cleanup.")
            return False
    names = {m["name"] for m in tags.get("models", [])}
    if LLM not in names and LLM + ":latest" not in names:
        log(f"WARNING: model {LLM} is not pulled. Run: ollama pull {LLM}. Transcripts will be pasted without cleanup.")
        return False
    return True

def cleanup(text, lang="en"):
    p = PROMPTS.get(lang, PROMPTS["en"])
    messages = [{"role": "system", "content": p["system"]}]
    for q, a in p["examples"]:
        messages += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
    messages.append({"role": "user", "content": text})
    body = json.dumps({
        "model": LLM, "stream": False, "think": False,
        "options": {"temperature": 0.1, "num_ctx": 8192}, "messages": messages,
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        out = json.load(r)["message"]["content"].strip()
    return out.strip('"\u201c\u201d\u300c\u300d ').strip()

# ---------- paste ----------
def paste(text):
    """Paste via the clipboard, then restore whatever text was on the clipboard before."""
    previous = subprocess.run(["pbpaste"], capture_output=True).stdout
    subprocess.run(["pbcopy"], input=text.encode(), check=True)
    kb = keyboard.Controller()
    time.sleep(0.05)
    with kb.pressed(keyboard.Key.cmd):
        kb.press("v"); kb.release("v")
    if previous:
        time.sleep(0.3)   # let the target app read the clipboard first
        subprocess.run(["pbcopy"], input=previous)

# ---------- main flow ----------
_ZH_PUNCT = str.maketrans({",": "，", ".": "。", "?": "？", "!": "！", ";": "；", ":": "："})

def tidy_raw(text, lang):
    """Minimal deterministic punctuation for transcripts that skip LLM cleanup."""
    text = text.strip()
    if not text:
        return text
    if lang == "zh":
        # half-width marks between CJK characters -> full-width; never touch marks inside Latin runs (3.5, e.g.)
        text = re.sub(r"(?<=[\u3400-\u9fff])[,.?!;:](?![0-9A-Za-z])|(?<![0-9])[,.?!;:](?=[\u3400-\u9fff])",
                      lambda m: m.group(0).translate(_ZH_PUNCT), text)
        text = re.sub(r"\s*([，。？！；：])\s*", r"\1", text)
        if text[-1] not in "。？！…」』）":
            text += "。"
    else:
        text = text[0].upper() + text[1:]
        if text[-1] not in ".?!\"')":
            text += "."
    return text

def process(audio):
    if audio is None or len(audio) < SAMPLE_RATE * 0.4:
        log("(too short, skipped)"); return
    t0 = time.time()
    raw, lang = transcribe(audio)
    if not raw:
        log("(nothing heard)"); return
    text = None
    if CLEANUP and len(raw) <= MAX_CLEANUP_CHARS:
        try:
            cleaned = cleanup(raw, lang)
            if faithful(raw, cleaned, lang):
                text = cleaned
            else:
                log("(cleanup output did not match what was said; pasting raw transcript)")
        except Exception as e:
            log(f"(cleanup unavailable: {e}; pasting raw transcript. Is Ollama running?)")
            if ollama_alive() is None:
                ensure_ollama()   # try to bring it back for the next recording
    if text is None:
        text = tidy_raw(raw, lang)
    paste(text)
    log(f"OK {time.time()-t0:.1f}s [{lang}] {text}")

def check_accessibility():
    ax = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")
    if ax.AXIsProcessTrusted():
        return
    log("Accessibility permission missing: the hotkey cannot be read and text cannot be pasted.")
    log("System Settings > Privacy & Security > Accessibility > enable the app running this script (Terminal, iTerm, Claude...), then rerun.")
    subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
    sys.exit(1)

def resolve_hotkey():
    name = KEY_ALIASES.get(HOTKEY.lower(), HOTKEY.lower())
    key = getattr(keyboard.Key, name, None)
    if key is not None:
        return key
    if len(HOTKEY) != 1:
        log(f"Unknown hotkey FLOW_HOTKEY={HOTKEY}. Try: right_option, right_cmd, right_ctrl, caps_lock, f13 ...")
        sys.exit(1)
    return keyboard.KeyCode.from_char(HOTKEY)

def single_instance():
    """Hold a localhost port for the process lifetime so a second copy cannot paste twice."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 48217)); sock.listen(1)
    except OSError:
        log("sotto is already running in another window. Quit it first."); sys.exit(1)
    return sock

class App:
    def __init__(self, key, recorder=None):
        self.key = key
        self.rec = recorder or Recorder()
        self.jobs = queue.Queue()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while True:
            audio = self.jobs.get()
            try:
                process(audio)
            except Exception as e:
                log(f"processing failed: {type(e).__name__}: {e}")
            finally:
                self.jobs.task_done()

    def on_press(self, k):
        if k != self.key or self.rec.stream is not None:
            return
        try:
            self.rec.start()
            pending = self.jobs.unfinished_tasks
            log("* recording..." + (f" ({pending} queued)" if pending else ""))
        except MicError as e:
            log(f"Microphone unavailable: {e}. Check Microphone permission / other apps using the mic, then try again.")

    def on_release(self, k):
        if k != self.key or self.rec.stream is None:
            return
        try:
            audio = self.rec.stop()
        except Exception as e:   # device vanished mid-recording; never let this kill the listener
            self.rec.stream = None
            log(f"recording failed: {e}"); return
        log("  processing...")
        self.jobs.put(audio)

def main():
    check_accessibility()
    key = resolve_hotkey()
    _guard = single_instance()
    check_microphone()
    log("Loading models...")
    transcribe(np.full(SAMPLE_RATE, 0.01, dtype=np.float32))
    if CLEANUP and ensure_ollama():
        try: cleanup("warm up", "en")
        except Exception as e:
            log(f"WARNING: Ollama answered but cleanup failed ({e}). Transcripts will be pasted without cleanup.")
    app = App(key)
    log(f"Ready. Hold [{HOTKEY.replace('_', ' ').title()}] to speak, release to paste. Ctrl+C to quit.")
    with keyboard.Listener(on_press=app.on_press, on_release=app.on_release) as l:
        l.join()

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
