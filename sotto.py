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

def transcribe(audio):
    """Returns (text, language). Language is auto-detected; Chinese is normalised to Traditional."""
    import mlx_whisper
    out = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER, language=LANG, verbose=None)
    lang = out.get("language") or LANG
    if lang not in LANGS:   # e.g. Chinese misdetected as Japanese/Cantonese -> redo as Chinese
        lang = "zh"
        out = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER, language=lang, verbose=None)
    text = out["text"].strip()
    if lang == "zh":
        text = to_traditional(text)
    return text, lang

def cleanup(text, lang="en"):
    p = PROMPTS.get(lang, PROMPTS["en"])
    messages = [{"role": "system", "content": p["system"]}]
    for q, a in p["examples"]:
        messages += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
    messages.append({"role": "user", "content": text})
    body = json.dumps({
        "model": LLM, "stream": False, "think": False,
        "options": {"temperature": 0.1}, "messages": messages,
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["message"]["content"].strip()

# ---------- paste ----------
def paste(text):
    subprocess.run(["pbcopy"], input=text.encode(), check=True)
    kb = keyboard.Controller()
    time.sleep(0.05)
    with kb.pressed(keyboard.Key.cmd):
        kb.press("v"); kb.release("v")

# ---------- main flow ----------
def process(audio):
    if audio is None or len(audio) < SAMPLE_RATE * 0.4:
        log("(too short, skipped)"); return
    t0 = time.time()
    raw, lang = transcribe(audio)
    if not raw:
        log("(nothing heard)"); return
    text = raw
    if CLEANUP:
        try:
            text = cleanup(raw, lang) or raw
        except Exception as e:
            log(f"cleanup failed, pasting raw transcript: {e}")
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

def main():
    check_accessibility()
    key = resolve_hotkey()
    rec = Recorder()
    busy = threading.Event()

    def on_press(k):
        if k == key and not busy.is_set() and rec.stream is None:
            try:
                rec.start(); log("* recording...")
            except MicError as e:
                log(f"Microphone unavailable: {e}. Check Microphone permission / other apps using the mic, then try again.")

    def on_release(k):
        if k == key and rec.stream is not None:
            audio = rec.stop()
            log("  processing...")
            def run():
                busy.set()
                try: process(audio)
                finally: busy.clear()
            threading.Thread(target=run, daemon=True).start()

    check_microphone()
    log("Loading models...")
    transcribe(np.zeros(SAMPLE_RATE, dtype=np.float32))
    if CLEANUP:
        try: cleanup("test", "en")
        except Exception as e:
            log(f"WARNING: cannot reach Ollama ({e}). Transcripts will be pasted without cleanup. Start it with: ollama serve")
    log(f"Ready. Hold [{HOTKEY.replace('_', ' ').title()}] to speak, release to paste. Ctrl+C to quit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as l:
        l.join()

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
