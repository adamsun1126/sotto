# flow - local push-to-talk dictation (English + Traditional Chinese)

Inspired by Wispr Flow. Hold **right Option**, speak, release: the speech is
transcribed, cleaned up (fillers, stutters and self-corrections removed,
punctuation added) and pasted at the cursor.

Everything runs on your Mac. Audio stays in memory. Nothing is logged or saved.

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
macOS will ask for two permissions the first time: **Microphone** and
**Accessibility** (System Settings > Privacy & Security > Accessibility: enable
the terminal app you run this from). Grant both, then run again.

Keep it running; in any app, hold right Option and speak.

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

## License
MIT
