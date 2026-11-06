# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

Dictée locale « appuyer pour parler » pour macOS, inspirée de Wispr Flow.

Maintenez **Option droite**, parlez, relâchez. Votre parole est transcrite, nettoyée (tics de langage, bégaiements et autocorrections supprimés, ponctuation ajoutée) puis collée à l'emplacement du curseur.

Tout s'exécute sur votre Mac. L'audio reste en mémoire. Rien n'est journalisé ni enregistré.

> La dictée prend actuellement en charge l'**anglais** et le **chinois traditionnel** (mélange possible).

- Reconnaissance vocale : [mlx-whisper](https://github.com/ml-explore/mlx-examples) (`whisper-large-v3-turbo`, Apple Silicon)
- Nettoyage : [Ollama](https://ollama.com) avec `qwen2.5:7b`
- La sortie en chinois est normalisée en traditionnel avec OpenCC

## Prérequis
macOS sur Apple Silicon.

## Installation (une seule fois)
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
Le modèle Whisper (~1,6 Go) se télécharge automatiquement au premier lancement.

## Lancer
```bash
./run.sh
```
Au premier lancement, macOS demande deux autorisations : **Microphone** et **Accessibilité** (Réglages Système > Confidentialité et sécurité > Accessibilité : activez l'app de terminal utilisée). Accordez les deux, puis relancez.

Laissez-le tourner. Dans n'importe quelle app, maintenez Option droite et parlez.

## Options
Variables d'environnement :

| Variable | Défaut | Signification |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | Touche à maintenir (`right_cmd`, `right_ctrl`, `caps_lock`, `f13`, ...) |
| `FLOW_LLM` | `qwen2.5:7b` | Modèle Ollama pour le nettoyage (`qwen2.5:3b` est plus léger mais moins bon sur les autocorrections) |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Modèle Whisper (`mlx-community/whisper-small-mlx` est plus rapide) |
| `FLOW_LANG` | auto | Forcer `zh` ou `en`. La détection automatique gère le mélange chinois/anglais |
| `FLOW_CLEANUP` | `1` | `0` colle la transcription brute sans nettoyage par LLM |

Exemple : `FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## Confidentialité
Aucune connexion réseau hormis le téléchargement initial des modèles. Aucun fichier écrit. Aucun historique. La seule trace de ce que vous avez dit est le texte collé dans votre app et le presse-papiers système.

## Licence
MIT
