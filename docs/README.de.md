# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

Lokales Push-to-Talk-Diktat für macOS, inspiriert von Wispr Flow.

**Rechte Option-Taste** gedrückt halten, sprechen, loslassen. Die Sprache wird transkribiert, bereinigt (Füllwörter, Stottern und Selbstkorrekturen entfernt, Satzzeichen ergänzt) und an der Cursorposition eingefügt.

Alles läuft auf deinem Mac. Audio bleibt im Arbeitsspeicher. Nichts wird protokolliert oder gespeichert.

> Das Diktat unterstützt derzeit **Englisch** und **traditionelles Chinesisch** (auch gemischt).

- Spracherkennung: [mlx-whisper](https://github.com/ml-explore/mlx-examples) (`whisper-large-v3-turbo`, Apple Silicon)
- Bereinigung: [Ollama](https://ollama.com) mit `qwen2.5:7b`
- Chinesische Ausgabe wird mit OpenCC auf traditionelle Zeichen normalisiert

## Voraussetzungen
macOS auf Apple Silicon.

## Installation (einmalig)
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
Das Whisper-Modell (~1,6 GB) wird beim ersten Start automatisch heruntergeladen.

## Starten
```bash
./run.sh
```
Beim ersten Start fragt macOS nach zwei Berechtigungen: **Mikrofon** und **Bedienungshilfen** (Systemeinstellungen > Datenschutz & Sicherheit > Bedienungshilfen: die verwendete Terminal-App aktivieren). Beide erteilen, dann erneut starten.

Laufen lassen. In jeder App rechte Option-Taste halten und sprechen.

## Optionen
Umgebungsvariablen:

| Variable | Standard | Bedeutung |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | Gehaltene Taste (`right_cmd`, `right_ctrl`, `caps_lock`, `f13`, ...) |
| `FLOW_LLM` | `qwen2.5:7b` | Ollama-Modell für die Bereinigung (`qwen2.5:3b` ist kleiner, aber schwächer bei Selbstkorrekturen) |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Whisper-Modell (`mlx-community/whisper-small-mlx` ist schneller) |
| `FLOW_LANG` | auto | `zh` oder `en` erzwingen. Die automatische Erkennung verarbeitet gemischtes Chinesisch/Englisch |
| `FLOW_CLEANUP` | `1` | `0` fügt das rohe Transkript ohne LLM-Bereinigung ein |

Beispiel: `FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## Datenschutz
Keine Netzwerkverbindungen außer dem einmaligen Modell-Download. Keine Dateien werden geschrieben. Kein Verlauf. Die einzige Spur des Gesagten ist der in deine App eingefügte Text und die Systemzwischenablage.

## Lizenz
MIT
