# repo-translate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**將 GitHub 倉庫文檔和程式碼註釋翻譯成你的語言。**

一個強大的 CLI 工具，可以克隆 GitHub 倉庫並將所有文檔（README、文檔）和程式碼註釋翻譯成目標語言。

[English](README.md) | [中文](README_zh-CN.md) | [日本語](README_ja.md) | [한국어](README_ko.md)

## 特性

- 🌍 **多語言支援**：支援翻譯成 10+ 種語言
- 🤖 **多提供商支援**：OpenAI、DeepSeek、智譜 (GLM)、Moonshot、通義千問、Ollama 以及任何相容 OpenAI 的 API
- 📝 **智慧解析**：從 Python、JavaScript/TypeScript、C/C++、Rust、Swift 中提取並翻譯註釋
- 📄 **Markdown 支援**：完整文檔翻譯，同時保留程式碼區塊
- ⚡ **批次翻譯**：高效的批次處理以加快翻譯速度
- 🔧 **靈活配置**：支援命令列參數、設定檔或環境變數

## 安裝

```bash
pip install repo-translate
```

## 快速開始

```bash
# 翻譯成中文（預設）
repo-translate karpathy/nanoGPT

# 翻譯成日語
repo-translate karpathy/nanoGPT --lang ja

# 使用智譜 AI（推薦台灣使用者使用）
repo-translate karpathy/nanoGPT --provider zhipu --api-key your-api-key

# 使用 DeepSeek
repo-translate karpathy/nanoGPT --provider deepseek --api-key sk-xxx
```

## 使用方法

### 基本翻譯

```bash
# 倉庫簡寫
repo-translate owner/repo

# 完整 URL
repo-translate https://github.com/owner/repo

# 指定目標語言
repo-translate owner/repo --lang ko
```

### LLM 提供商

```bash
# OpenAI（預設）
repo-translate owner/repo --provider openai --api-key sk-xxx

# DeepSeek
repo-translate owner/repo --provider deepseek --api-key sk-xxx

# 智譜 AI
repo-translate owner/repo --provider zhipu --api-key xxx.xxx

# Moonshot（月之暗面）
repo-translate owner/repo --provider moonshot --api-key sk-xxx

# 通義千問
repo-translate owner/repo --provider qwen --api-key sk-xxx

# Ollama（本地）
repo-translate owner/repo --provider ollama --model llama3

# 自訂 OpenAI 相容 API
repo-translate owner/repo --provider custom --base-url https://api.example.com/v1 --api-key xxx
```

### 配置

建立 `.repo-translate.json` 設定檔：

```bash
repo-translate config init
```

設定範例：

```json
{
  "provider": "zhipu",
  "model": "glm-4-flash",
  "target_lang": "zh-tw",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "api_key": "your-api-key",
  "batch_size": 5
}
```

**配置優先順序**（從高到低）：

1. 命令列參數
2. 專案設定檔（`.repo-translate.json`）
3. 全域配置（`~/.local/share/repo_translate/config.json`）
4. 環境變數
5. 預設值

## 支援的提供商

| 提供商 | 預設模型 | API 端點 |
|--------|---------|----------|
| `openai` | gpt-4o-mini | api.openai.com/v1 |
| `deepseek` | deepseek-chat | api.deepseek.com/v1 |
| `zhipu` | glm-4-flash | open.bigmodel.cn/api/paas/v4 |
| `moonshot` | moonshot-v1-8k | api.moonshot.cn/v1 |
| `qwen` | qwen-turbo | dashscope.aliyuncs.com/compatible-mode/v1 |
| `ollama` | llama3 | localhost:11434/v1 |
| `custom` | gpt-4o-mini | （使用者提供） |

## 支援的語言

| 代碼 | 語言 | 代碼 | 語言 |
|------|------|------|------|
| `zh` | 中文 | `en` | 英語 |
| `ja` | 日語 | `ko` | 韓語 |
| `fr` | 法語 | `de` | 德語 |
| `es` | 西班牙語 | `pt` | 葡萄牙語 |
| `ru` | 俄語 | `it` | 義大利語 |
| `ar` | 阿拉伯語 | `th` | 泰語 |
| `vi` | 越南語 | `id` | 印尼語 |

## 支援的檔案類型

| 類型 | 副檔名 | 翻譯內容 |
|------|--------|----------|
| Markdown | `.md`, `.markdown` | 完整文檔（保留程式碼區塊） |
| Python | `.py`, `.pyw` | 註釋、文檔字串 |
| JavaScript | `.js`, `.jsx`, `.mjs` | 註釋、JSDoc |
| TypeScript | `.ts`, `.tsx` | 註釋、JSDoc |
| C/C++ | `.c`, `.h`, `.cpp`, `.hpp` | 註釋、Doxygen |
| Rust | `.rs` | 註釋、文檔註釋（`///`、`//!`） |
| Swift | `.swift` | 註釋、文檔 |

## 輸出

翻譯完成後，你會得到：

```
./repo_name/           # 原始克隆的倉庫
./repo_name_translated/  # 翻譯後的倉庫
```

## 系統需求

- Python 3.10+
- 你選擇的 LLM 提供商的 API 金鑰

## 授權條款

MIT 授權條款 - 詳見 [LICENSE](LICENSE)。

## 貢獻

歡迎貢獻！請隨時提交 Pull Request。

## 致謝

- 使用 [Typer](https://typer.tiangolo.com/) 构建 CLI
- 使用 [tree-sitter](https://tree-sitter.github.io/tree-sitter/) 進行程式碼解析
- 由各種 LLM 提供商提供支援
