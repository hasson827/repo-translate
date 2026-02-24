# repo-translate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**将 GitHub 仓库文档和代码注释翻译成你的语言。**

一个强大的 CLI 工具，可以克隆 GitHub 仓库并将所有文档（README、文档）和代码注释翻译成目标语言。

[English](README.md) | [繁體中文](README_zh-TW.md) | [日本語](README_ja.md) | [한국어](README_ko.md)

## 特性

- 🌍 **多语言支持**：支持翻译成 10+ 种语言
- 🤖 **多提供商支持**：OpenAI、DeepSeek、智谱 (GLM)、Moonshot、通义千问、Ollama 以及任何兼容 OpenAI 的 API
- 📝 **智能解析**：从 Python、JavaScript/TypeScript、C/C++、Rust、Swift 中提取并翻译注释
- 📄 **Markdown 支持**：完整文档翻译，同时保留代码块
- ⚡ **批量翻译**：高效的批处理以加快翻译速度
- 🔧 **灵活配置**：支持命令行参数、配置文件或环境变量

## 安装

```bash
pip install repo-translate
```

## 快速开始

```bash
# 翻译成中文（默认）
repo-translate karpathy/nanoGPT

# 翻译成日语
repo-translate karpathy/nanoGPT --lang ja

# 使用智谱 AI（推荐中国用户使用）
repo-translate karpathy/nanoGPT --provider zhipu --api-key your-api-key

# 使用 DeepSeek
repo-translate karpathy/nanoGPT --provider deepseek --api-key sk-xxx
```

## 使用方法

### 基本翻译

```bash
# 仓库简写
repo-translate owner/repo

# 完整 URL
repo-translate https://github.com/owner/repo

# 指定目标语言
repo-translate owner/repo --lang ko
```

### LLM 提供商

```bash
# OpenAI（默认）
repo-translate owner/repo --provider openai --api-key sk-xxx

# DeepSeek
repo-translate owner/repo --provider deepseek --api-key sk-xxx

# 智谱 AI
repo-translate owner/repo --provider zhipu --api-key xxx.xxx

# Moonshot（月之暗面）
repo-translate owner/repo --provider moonshot --api-key sk-xxx

# 通义千问
repo-translate owner/repo --provider qwen --api-key sk-xxx

# Ollama（本地）
repo-translate owner/repo --provider ollama --model llama3

# 自定义 OpenAI 兼容 API
repo-translate owner/repo --provider custom --base-url https://api.example.com/v1 --api-key xxx
```

### 配置

创建 `.repo-translate.json` 配置文件：

```bash
repo-translate config init
```

配置示例：

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

**配置优先级**（从高到低）：

1. 命令行参数
2. 项目配置文件（`.repo-translate.json`）
3. 全局配置（`~/.local/share/repo_translate/config.json`）
4. 环境变量
5. 默认值

### CLI 命令

```bash
# 初始化配置文件
repo-translate config init

# 设置全局提供商配置
repo-translate config set zhipu --api-key xxx --model glm-4-flash

# 显示当前配置
repo-translate config show

# 列出支持的提供商
repo-translate providers

# 列出支持的语言
repo-translate languages

# 试运行（预览不修改）
repo-translate owner/repo --dry-run
```

### 环境变量

```bash
export REPO_TRANSLATE_API_KEY=your-api-key
export REPO_TRANSLATE_PROVIDER=zhipu
export REPO_TRANSLATE_MODEL=glm-4-flash
repo-translate owner/repo
```

## 支持的提供商

| 提供商 | 默认模型 | API 端点 |
|--------|---------|----------|
| `openai` | gpt-4o-mini | api.openai.com/v1 |
| `deepseek` | deepseek-chat | api.deepseek.com/v1 |
| `zhipu` | glm-4-flash | open.bigmodel.cn/api/paas/v4 |
| `moonshot` | moonshot-v1-8k | api.moonshot.cn/v1 |
| `qwen` | qwen-turbo | dashscope.aliyuncs.com/compatible-mode/v1 |
| `ollama` | llama3 | localhost:11434/v1 |
| `custom` | gpt-4o-mini | （用户提供） |

## 支持的语言

| 代码 | 语言 | 代码 | 语言 |
|------|------|------|------|
| `zh` | 中文 | `en` | 英语 |
| `ja` | 日语 | `ko` | 韩语 |
| `fr` | 法语 | `de` | 德语 |
| `es` | 西班牙语 | `pt` | 葡萄牙语 |
| `ru` | 俄语 | `it` | 意大利语 |
| `ar` | 阿拉伯语 | `th` | 泰语 |
| `vi` | 越南语 | `id` | 印尼语 |

## 支持的文件类型

| 类型 | 扩展名 | 翻译内容 |
|------|--------|----------|
| Markdown | `.md`, `.markdown` | 完整文档（保留代码块） |
| Python | `.py`, `.pyw` | 注释、文档字符串 |
| JavaScript | `.js`, `.jsx`, `.mjs` | 注释、JSDoc |
| TypeScript | `.ts`, `.tsx` | 注释、JSDoc |
| C/C++ | `.c`, `.h`, `.cpp`, `.hpp` | 注释、Doxygen |
| Rust | `.rs` | 注释、文档注释（`///`、`//!`） |
| Swift | `.swift` | 注释、文档 |

## 输出

翻译完成后，你会得到：

```
./repo_name/           # 原始克隆的仓库
./repo_name_translated/  # 翻译后的仓库
```

## 系统要求

- Python 3.10+
- 你选择的 LLM 提供商的 API 密钥

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 致谢

- 使用 [Typer](https://typer.tiangolo.com/) 构建 CLI
- 使用 [tree-sitter](https://tree-sitter.github.io/tree-sitter/) 进行代码解析
- 由各种 LLM 提供商提供支持
