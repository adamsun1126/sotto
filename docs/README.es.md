# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

Dictado local pulsar-para-hablar para macOS, inspirado en Wispr Flow.

Mantén pulsada la **Option derecha**, habla y suelta. Tu voz se transcribe, se limpia (sin muletillas, tartamudeos ni autocorrecciones, con puntuación) y se pega donde está el cursor.

Todo se ejecuta en tu Mac. El audio permanece en memoria. No se registra ni se guarda nada.

> Actualmente el dictado admite **inglés** y **chino tradicional** (también mezclados).

- Voz a texto: [mlx-whisper](https://github.com/ml-explore/mlx-examples) (`whisper-large-v3-turbo`, Apple Silicon)
- Limpieza: [Ollama](https://ollama.com) ejecutando `qwen2.5:7b`
- La salida en chino se normaliza a tradicional con OpenCC

## Requisitos
macOS con Apple Silicon.

## Instalación (una vez)
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
El modelo Whisper (~1,6 GB) se descarga automáticamente en la primera ejecución.

## Ejecutar
```bash
./run.sh
```
La primera vez macOS pide dos permisos: **Micrófono** y **Accesibilidad** (Ajustes del Sistema > Privacidad y seguridad > Accesibilidad: activa la app de terminal desde la que lo ejecutas). Concede ambos y vuelve a ejecutar.

Déjalo en marcha. En cualquier app, mantén pulsada la Option derecha y habla.

## Opciones
Variables de entorno:

| Variable | Por defecto | Significado |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | Tecla a mantener (`right_cmd`, `right_ctrl`, `caps_lock`, `f13`, ...) |
| `FLOW_LLM` | `qwen2.5:7b` | Modelo de Ollama para la limpieza (`qwen2.5:3b` es más pequeño pero peor con autocorrecciones) |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Modelo Whisper (`mlx-community/whisper-small-mlx` es más rápido) |
| `FLOW_LANG` | auto | Forzar `zh` o `en`. La detección automática gestiona chino/inglés mezclados |
| `FLOW_CLEANUP` | `1` | `0` pega la transcripción sin limpieza por LLM |

Ejemplo: `FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## Privacidad
Sin conexiones de red salvo la descarga inicial de los modelos. No se escriben archivos. Sin historial. El único rastro de lo que dijiste es el texto pegado en tu app y el portapapeles del sistema.

## Licencia
MIT
