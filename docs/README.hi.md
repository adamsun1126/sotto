# sotto

[English](../README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [हिन्दी](README.hi.md)

macOS के लिए लोकल पुश-टू-टॉक डिक्टेशन, Wispr Flow से प्रेरित।

**दायाँ Option** दबाए रखें, बोलें, छोड़ दें। आपकी आवाज़ टेक्स्ट में बदलती है, साफ़ होती है (फ़िलर शब्द, हकलाहट और खुद के सुधार हटाकर, विराम चिह्न जोड़कर) और कर्सर की जगह पर पेस्ट हो जाती है।

सब कुछ आपके Mac पर चलता है। ऑडियो सिर्फ़ मेमोरी में रहता है। कुछ भी लॉग या सेव नहीं होता।

> फ़िलहाल डिक्टेशन **अंग्रेज़ी** और **पारंपरिक चीनी** को सपोर्ट करता है (मिश्रित भी चलेगा)।

- स्पीच-टू-टेक्स्ट: [mlx-whisper](https://github.com/ml-explore/mlx-examples) (`whisper-large-v3-turbo`, Apple Silicon)
- सफ़ाई: [Ollama](https://ollama.com) पर `qwen2.5:7b`
- चीनी आउटपुट OpenCC से पारंपरिक लिपि में बदला जाता है

## आवश्यकताएँ
Apple Silicon वाला macOS।

## इंस्टॉल (एक बार)
```bash
brew install uv ollama
ollama pull qwen2.5:7b
```
Whisper मॉडल (~1.6 GB) पहली बार चलाने पर अपने आप डाउनलोड हो जाता है।

## चलाएँ
```bash
./run.sh
```
पहली बार macOS दो अनुमतियाँ माँगता है: **माइक्रोफ़ोन** और **Accessibility** (System Settings > Privacy & Security > Accessibility: जिस टर्मिनल ऐप से चला रहे हैं उसे चालू करें)। दोनों दें, फिर दोबारा चलाएँ।

इसे चलता रहने दें। किसी भी ऐप में दायाँ Option दबाए रखें और बोलें।

## विकल्प
एनवायरनमेंट वेरिएबल:

| वेरिएबल | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `FLOW_HOTKEY` | `right_option` | दबाए रखने वाली कुंजी (`right_cmd`, `right_ctrl`, `caps_lock`, `f13`, ...) |
| `FLOW_LLM` | `qwen2.5:7b` | सफ़ाई के लिए Ollama मॉडल (`qwen2.5:3b` छोटा है पर खुद के सुधारों में कमज़ोर) |
| `FLOW_WHISPER` | `mlx-community/whisper-large-v3-turbo` | Whisper मॉडल (`mlx-community/whisper-small-mlx` तेज़ है) |
| `FLOW_LANG` | auto | `zh` या `en` ज़बरदस्ती सेट करें। ऑटो-डिटेक्ट मिश्रित चीनी/अंग्रेज़ी संभाल लेता है |
| `FLOW_CLEANUP` | `1` | `0` से LLM सफ़ाई के बिना कच्चा ट्रांसक्रिप्ट पेस्ट होता है |

उदाहरण: `FLOW_HOTKEY=f13 FLOW_LLM=qwen2.5:3b ./run.sh`

## गोपनीयता
एक बार के मॉडल डाउनलोड के अलावा कोई नेटवर्क कॉल नहीं। कोई फ़ाइल नहीं लिखी जाती। कोई इतिहास नहीं। आपने जो कहा उसका एकमात्र निशान आपके ऐप में पेस्ट हुआ टेक्स्ट और सिस्टम क्लिपबोर्ड है।

## लाइसेंस
MIT
