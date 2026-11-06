# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

Ditado local do tipo aperte-para-falar para macOS, inspirado no Wispr Flow.

Segure a **Option direita**, fale e solte. Sua fala é transcrita, limpa (sem vícios de linguagem, gagueiras e autocorreções, com pontuação) e colada na posição do cursor.

Tudo roda no seu Mac. O áudio fica apenas na memória. Nada é registrado ou salvo.

> No momento o ditado suporta **inglês** e **chinês tradicional** (misturados também).

- Fala para texto: [mlx-whisper](https://github.com/ml-explore/mlx-examples) (`whisper-large-v3-turbo`, Apple Silicon)
- Limpeza: [Ollama](https://ollama.com) rodando `qwen2.5:7b`
- A saída em chinês é normalizada para tradicional com OpenCC

## Requisitos
macOS com Apple Silicon.

## Instalação (uma vez)
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
O modelo Whisper (~1,6 GB) é baixado automaticamente na primeira execução.

## Executar
```bash
./run.sh
```
Na primeira vez o macOS pede duas permissões: **Microfone** e **Acessibilidade** (Ajustes do Sistema > Privacidade e Segurança > Acessibilidade: ative o app de terminal usado para executar). Conceda as duas e execute novamente.

Deixe rodando. Em qualquer app, segure a Option direita e fale.

## Opções
Variáveis de ambiente:

| Variável | Padrão | Significado |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | Tecla a segurar (`right_cmd`, `right_ctrl`, `caps_lock`, `f13`, ...) |
| `FLOW_LLM` | `qwen2.5:7b` | Modelo do Ollama para limpeza (`qwen2.5:3b` é menor, mas pior com autocorreções) |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Modelo Whisper (`mlx-community/whisper-small-mlx` é mais rápido) |
| `FLOW_LANG` | auto | Forçar `zh` ou `en`. A detecção automática lida com chinês/inglês misturados |
| `FLOW_CLEANUP` | `1` | `0` cola a transcrição bruta sem limpeza por LLM |

Exemplo: `FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## Privacidade
Nenhuma conexão de rede além do download inicial dos modelos. Nenhum arquivo é gravado. Sem histórico. O único rastro do que você disse é o texto colado no seu app e a área de transferência do sistema.

## Licença
MIT
