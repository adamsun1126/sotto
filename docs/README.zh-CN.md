# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

macOS 上的本地按住说话听写工具，灵感来自 Wispr Flow。

按住 **右 Option** 说话，松开后语音会被转成文字、整理干净（去掉口头禅、结巴与改口，补上标点），然后粘贴到光标所在位置。

全部在你的 Mac 上运行。音频只保留在内存中，不记录、不保存任何内容。

> 听写目前支持 **英文** 与 **繁体中文**（中英混合也可以）。简体中文语音会被识别，但输出为繁体。

- 语音识别：[mlx-whisper](https://github.com/ml-explore/mlx-examples)（`whisper-large-v3-turbo`，Apple Silicon）
- 文字整理：[Ollama](https://ollama.com) 运行 `qwen2.5:7b`
- 中文输出通过 OpenCC 统一转为繁体

## 要求
Apple Silicon 的 macOS。

## 安装（一次）
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
Whisper 模型（约 1.6 GB）会在首次运行时自动下载。

## 运行
```bash
./run.sh
```
首次运行 macOS 会请求两个权限：**麦克风** 与 **辅助功能**（系统设置 > 隐私与安全性 > 辅助功能：开启你用来运行的终端 App）。两个都授权后再运行一次。

让它保持运行。在任何 App 里按住右 Option 说话即可。

## 选项
环境变量：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | 按住的按键（`right_cmd`、`right_ctrl`、`caps_lock`、`f13`…） |
| `FLOW_LLM` | `qwen2.5:7b` | 整理用的 Ollama 模型（`qwen2.5:3b` 更小，但处理改口较差） |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Whisper 模型（`mlx-community/whisper-small-mlx` 更快） |
| `FLOW_LANG` | auto | 强制 `zh` 或 `en`。自动检测可处理中英混合 |
| `FLOW_CLEANUP` | `1` | 设为 `0` 直接粘贴原始转写，不经 LLM 整理 |

示例：`FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## 隐私
除一次性的模型下载外没有任何网络请求。不写入文件、没有历史记录。你说过的话唯一留下的痕迹，是粘贴进 App 的文字与系统剪贴板。

## 许可
MIT
