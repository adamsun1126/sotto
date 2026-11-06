# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

macOS용 로컬 푸시 투 토크 받아쓰기 도구. Wispr Flow에서 영감을 받았습니다.

**오른쪽 Option**을 누른 채 말하고 손을 떼세요. 음성이 텍스트로 변환되고 정리된 뒤(군말, 말더듬, 정정 제거, 문장 부호 추가) 커서 위치에 붙여넣어집니다.

모든 처리가 Mac에서 이루어집니다. 오디오는 메모리에만 머물며, 아무것도 기록되거나 저장되지 않습니다.

> 현재 받아쓰기는 **영어**와 **번체 중국어**를 지원합니다(혼용 가능).

- 음성 인식: [mlx-whisper](https://github.com/ml-explore/mlx-examples) (`whisper-large-v3-turbo`, Apple Silicon)
- 정리: [Ollama](https://ollama.com)에서 실행되는 `qwen2.5:7b`
- 중국어 출력은 OpenCC로 번체로 통일

## 요구 사항
Apple Silicon macOS.

## 설치(한 번만)
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
Whisper 모델(약 1.6 GB)은 첫 실행 시 자동으로 내려받습니다.

## 실행
```bash
./run.sh
```
첫 실행 시 macOS가 두 가지 권한을 요청합니다: **마이크**와 **손쉬운 사용**(시스템 설정 > 개인정보 보호 및 보안 > 손쉬운 사용: 실행에 사용하는 터미널 앱을 켜기). 둘 다 허용한 뒤 다시 실행하세요.

계속 실행해 두고, 어떤 앱에서든 오른쪽 Option을 누른 채 말하면 됩니다.

## 옵션
환경 변수:

| 변수 | 기본값 | 의미 |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | 누르고 있을 키(`right_cmd`, `right_ctrl`, `caps_lock`, `f13` 등) |
| `FLOW_LLM` | `qwen2.5:7b` | 정리에 쓰는 Ollama 모델(`qwen2.5:3b`은 더 작지만 정정 처리가 약함) |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Whisper 모델(`mlx-community/whisper-small-mlx`이 더 빠름) |
| `FLOW_LANG` | auto | `zh` 또는 `en`으로 고정. 자동 감지는 중영 혼용도 처리 |
| `FLOW_CLEANUP` | `1` | `0`이면 LLM 정리 없이 원문 전사를 붙여넣기 |

예: `FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## 개인정보
최초 모델 다운로드 외에는 네트워크 통신이 없습니다. 파일 기록도, 기록 보관도 없습니다. 말한 내용의 유일한 흔적은 앱에 붙여넣어진 텍스트와 시스템 클립보드뿐입니다.

## 라이선스
MIT
