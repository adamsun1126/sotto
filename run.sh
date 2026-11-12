#!/bin/zsh
# Run sotto (it starts Ollama itself if needed).
export PATH=/opt/homebrew/bin:$PATH
cd "$(dirname "$0")"
exec uv run sotto.py "$@"
