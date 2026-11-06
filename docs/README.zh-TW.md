# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

macOS 上的本機按住說話聽寫工具，靈感來自 Wispr Flow。

按住 **右 Option** 說話，放開後語音會被轉成文字、整理乾淨（去掉口頭禪、結巴與改口，補上標點），然後貼到游標所在位置。

全部在你的 Mac 上執行。音訊只留在記憶體，不記錄、不儲存任何東西。

> 聽寫目前支援 **英文** 與 **繁體中文**（中英夾雜也可以）。

- 語音辨識：[mlx-whisper](https://github.com/ml-explore/mlx-examples)（`whisper-large-v3-turbo`，Apple Silicon）
- 文字整理：[Ollama](https://ollama.com) 執行 `qwen2.5:7b`
- 中文輸出以 OpenCC 統一轉為繁體

## 需求
Apple Silicon 的 macOS。

## 安裝（一次）
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
Whisper 模型（約 1.6 GB）會在第一次執行時自動下載。

## 執行
```bash
./run.sh
```
第一次執行 macOS 會要求兩個權限：**麥克風** 與 **輔助使用**（系統設定 > 隱私權與安全性 > 輔助使用：開啟你用來執行的終端機 App）。兩個都授權後再執行一次。

讓它持續執行。在任何 App 裡按住右 Option 說話即可。

## 選項
環境變數：

| 變數 | 預設值 | 說明 |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | 按住的按鍵（`right_cmd`、`right_ctrl`、`caps_lock`、`f13`…） |
| `FLOW_LLM` | `qwen2.5:7b` | 整理用的 Ollama 模型（`qwen2.5:3b` 較小，但處理改口較差） |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Whisper 模型（`mlx-community/whisper-small-mlx` 較快） |
| `FLOW_LANG` | auto | 強制 `zh` 或 `en`。自動偵測可處理中英夾雜 |
| `FLOW_CLEANUP` | `1` | 設 `0` 直接貼上逐字稿，不經 LLM 整理 |

範例：`FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## 隱私
除了一次性的模型下載外沒有任何網路連線。不寫入檔案、沒有歷史紀錄。你說過的話唯一留下的痕跡，是貼進 App 的文字與系統剪貼簿。

## 授權
MIT
