# repo-translate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Translate GitHub repository documentation and code comments to your language.**

A powerful CLI tool that clones a GitHub repository and translates all documentation (README, docs) and code comments into your target language using LLM providers.

[中文](README_zh-CN.md) | [繁體中文](README_zh-TW.md) | [日本語](README_ja.md) | [한국어](README_ko.md)

## Features

- 🌍 **Multi-language Support**: Translate to 10+ languages
- 🤖 **Multi-provider Support**: OpenAI, DeepSeek, Zhipu (GLM), Moonshot, Qwen, Ollama, and any OpenAI-compatible API
- 📝 **Smart Parsing**: Extracts and translates comments from Python, JavaScript/TypeScript, C/C++, Rust, Swift
- 📄 **Markdown Support**: Full document translation while preserving code blocks
- ⚡ **Batch Translation**: Efficient batch processing for faster translations
- 🔧 **Flexible Configuration**: CLI args, config files, or environment variables

## Installation

```bash
pip install repo-translate
```

## Quick Start

```bash
# Translate to Chinese (default)
repo-translate translate karpathy/nanoGPT

# Translate to Japanese
repo-translate translate karpathy/nanoGPT --lang ja

# Using Zhipu AI (recommended for Chinese users)
repo-translate translate karpathy/nanoGPT --provider zhipu --api-key your-api-key

# Using DeepSeek
repo-translate translate karpathy/nanoGPT --provider deepseek --api-key sk-xxx
```

## Usage

### Basic Translation

```bash
# Repository shorthand
repo-translate translate owner/repo

# Full URL
repo-translate translate https://github.com/owner/repo

# Specify target language
repo-translate translate owner/repo --lang ko
```

### LLM Providers

```bash
# OpenAI (default)
repo-translate translate owner/repo --provider openai --api-key sk-xxx

# DeepSeek
repo-translate translate owner/repo --provider deepseek --api-key sk-xxx

# Zhipu AI (智谱)
repo-translate translate owner/repo --provider zhipu --api-key xxx.xxx

# Moonshot (月之暗面)
repo-translate translate owner/repo --provider moonshot --api-key sk-xxx

# Qwen (通义千问)
repo-translate translate owner/repo --provider qwen --api-key sk-xxx

# Ollama (local)
repo-translate translate owner/repo --provider ollama --model llama3

# Custom OpenAI-compatible API
repo-translate translate owner/repo --provider custom --base-url https://api.example.com/v1 --api-key xxx
```

### Configuration

Create a `.repo-translate.json` file:

```bash
repo-translate config init
```

Example configuration:

```json
{
  "provider": "zhipu",
  "model": "glm-4-flash",
  "target_lang": "zh",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "api_key": "your-api-key",
  "batch_size": 5
}
```

**Configuration Priority** (highest to lowest):

1. CLI arguments
2. Project config file (`.repo-translate.json`)
3. Global config (`~/.local/share/repo_translate/config.json`)
4. Environment variables
5. Default values

### CLI Commands

```bash
# Initialize config file
repo-translate config init

# Set global provider config
repo-translate config set zhipu --api-key xxx --model glm-4-flash

# Show current configuration
repo-translate config show

# List supported providers
repo-translate providers

# List supported languages
repo-translate languages

# Dry run (preview without changes)
repo-translate translate owner/repo --dry-run
```

### Environment Variables

```bash
export REPO_TRANSLATE_API_KEY=your-api-key
export REPO_TRANSLATE_PROVIDER=zhipu
export REPO_TRANSLATE_MODEL=glm-4-flash
repo-translate translate owner/repo
```

## Supported Providers

| Provider | Default Model | Base URL |
|----------|--------------|----------|
| `openai` | gpt-4o-mini | api.openai.com/v1 |
| `deepseek` | deepseek-chat | api.deepseek.com/v1 |
| `zhipu` | glm-4-flash | open.bigmodel.cn/api/paas/v4 |
| `moonshot` | moonshot-v1-8k | api.moonshot.cn/v1 |
| `qwen` | qwen-turbo | dashscope.aliyuncs.com/compatible-mode/v1 |
| `ollama` | llama3 | localhost:11434/v1 |
| `custom` | gpt-4o-mini | (user-provided) |

## Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| `zh` | Chinese (中文) | `en` | English |
| `ja` | Japanese (日本語) | `ko` | Korean (한국어) |
| `fr` | French | `de` | German |
| `es` | Spanish | `pt` | Portuguese |
| `ru` | Russian | `it` | Italian |
| `ar` | Arabic | `th` | Thai |
| `vi` | Vietnamese | `id` | Indonesian |

## Supported File Types

| Type | Extensions | What's Translated |
|------|------------|-------------------|
| Markdown | `.md`, `.markdown` | Full document (code blocks preserved) |
| Python | `.py`, `.pyw` | Comments, docstrings |
| JavaScript | `.js`, `.jsx`, `.mjs` | Comments, JSDoc |
| TypeScript | `.ts`, `.tsx` | Comments, JSDoc |
| C/C++ | `.c`, `.h`, `.cpp`, `.hpp` | Comments, Doxygen |
| Rust | `.rs` | Comments, doc comments (`///`, `//!`) |
| Swift | `.swift` | Comments, documentation |

## Output

After translation, you'll find:

```
./repo_name/           # Original cloned repository
./repo_name_translated/  # Translated repository
```

## Requirements

- Python 3.10+
- API key for your chosen LLM provider

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Uses [tree-sitter](https://tree-sitter.github.io/tree-sitter/) for code parsing
- Powered by various LLM providers
