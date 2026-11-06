# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

macOS 向けのローカル実行プッシュトゥトーク音声入力ツール。Wispr Flow に着想を得ています。

**右 Option** を押しながら話し、離すだけ。音声は文字起こしされ、整形（フィラー・言い直し・どもりの除去、句読点の付与）されて、カーソル位置に貼り付けられます。

すべてあなたの Mac 上で動作します。音声はメモリ上にのみ存在し、何も記録・保存されません。

> 現在の対応言語は **英語** と **繁体字中国語** です（混在も可）。

- 音声認識：[mlx-whisper](https://github.com/ml-explore/mlx-examples)（`whisper-large-v3-turbo`、Apple Silicon）
- 整形：[Ollama](https://ollama.com) 上の `qwen2.5:7b`
- 中国語の出力は OpenCC で繁体字に統一

## 必要環境
Apple Silicon 搭載の macOS。

## インストール（初回のみ）
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
Whisper モデル（約 1.6 GB）は初回実行時に自動でダウンロードされます。

## 実行
```bash
./run.sh
```
初回実行時に macOS が 2 つの権限を求めます：**マイク** と **アクセシビリティ**（システム設定 > プライバシーとセキュリティ > アクセシビリティ：実行に使うターミナルアプリを有効化）。両方許可してから再実行してください。

起動したままにして、どのアプリでも右 Option を押しながら話してください。

## オプション
環境変数：

| 変数 | 既定値 | 意味 |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | 押し続けるキー（`right_cmd`、`right_ctrl`、`caps_lock`、`f13` など） |
| `FLOW_LLM` | `qwen2.5:7b` | 整形に使う Ollama モデル（`qwen2.5:3b` は軽量だが言い直しの処理が弱い） |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Whisper モデル（`mlx-community/whisper-small-mlx` は高速） |
| `FLOW_LANG` | auto | `zh` または `en` に固定。自動判定は中英混在にも対応 |
| `FLOW_CLEANUP` | `1` | `0` で LLM 整形なしに生の文字起こしを貼り付け |

例：`FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## プライバシー
初回のモデルダウンロード以外にネットワーク通信はありません。ファイル書き込みも履歴もなし。話した内容が残るのは、アプリに貼り付けられたテキストとシステムのクリップボードだけです。

## ライセンス
MIT
