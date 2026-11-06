#!/bin/zsh
# Start Ollama if needed, then run flow.
export PATH=/opt/homebrew/bin:$PATH
cd "$(dirname "$0")"
pgrep -x ollama >/dev/null || (ollama serve >/dev/null 2>&1 &) && sleep 1
exec uv run flow.py "$@"
