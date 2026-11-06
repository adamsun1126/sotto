# sotto

**English** · [繁體中文](docs/README.zh-TW.md) · [简体中文](docs/README.zh-CN.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Español](docs/README.es.md) · [Português](docs/README.pt-BR.md) · [Français](docs/README.fr.md) · [Deutsch](docs/README.de.md) · [Русский](docs/README.ru.md) · [हिन्दी](docs/README.hi.md)

Local, private push-to-talk dictation for macOS: an open-source Wispr Flow alternative. Speech-to-text with Whisper, cleaned up by a local LLM, pasted at your cursor. No cloud, no account, no logs.

Hold **right Option**, speak, release. Your speech is transcribed, cleaned up
(fillers, stutters and self-corrections removed, punctuation added) and pasted
at the cursor.

Everything runs on your Mac. Audio stays in memory. Nothing is logged or saved.

> Dictation currently supports **English** and **Traditional Chinese** (mixed is fine).

- Speech-to-text: [mlx-whisper](https://github.com/ml-explore/mlx-examples) (`whisper-large-v3-turbo`, Apple Silicon)
- Cleanup: [Ollama](https://ollama.com) running `qwen2.5:7b`
- Chinese output is normalised to Traditional with OpenCC

## Requirements
macOS on Apple Silicon.

## Install (once)
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
The Whisper model (~1.6 GB) downloads automatically on first run.

## Run
```bash
./run.sh
```
macOS asks for two permissions the first time: **Microphone** and
**Accessibility** (System Settings > Privacy & Security > Accessibility: enable
the terminal app you run this from). Grant both, then run again.

Keep it running. In any app, hold right Option and speak.

## Options
Environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | Key to hold (`right_cmd`, `right_ctrl`, `caps_lock`, `f13`, ...) |
| `FLOW_LLM` | `qwen2.5:7b` | Ollama model for cleanup (`qwen2.5:3b` is smaller but worse at self-corrections) |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Whisper model (`mlx-community/whisper-small-mlx` is faster) |
| `FLOW_LANG` | auto | Force `zh` or `en`. Auto-detect handles mixed Chinese/English |
| `FLOW_CLEANUP` | `1` | `0` pastes the raw transcript without LLM cleanup |

Example: `FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## Privacy
No network calls except the one-time model downloads. No files written. No
history. The only trace of what you said is the text pasted into your app and
the system clipboard.

## Why another dictation tool?
Wispr Flow, Superwhisper and macOS dictation are great, but they either send
audio to the cloud, keep a history, or are closed source. sotto is the minimal
version: open-source voice typing for macOS that runs Whisper and an LLM
locally, with push-to-talk and automatic cleanup, and nothing else.

## License
MIT
