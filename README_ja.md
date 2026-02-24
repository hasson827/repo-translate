# repo-translate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**GitHubリポジトリのドキュメントとコードコメントをあなたの言語に翻訳します。**

GitHubリポジトリをクローンし、すべてのドキュメント（README、docs）とコードコメントをターゲット言語に翻訳する強力なCLIツールです。

[English](README.md) | [中文](README_zh-CN.md) | [繁體中文](README_zh-TW.md) | [한국어](README_ko.md)

## 特徴

- 🌍 **多言語対応**: 10以上の言語に翻訳可能
- 🤖 **複数プロバイダー対応**: OpenAI、DeepSeek、Zhipu (GLM)、Moonshot、Qwen、Ollama、およびOpenAI互換API
- 📝 **スマート解析**: Python、JavaScript/TypeScript、C/C++、Rust、Swiftからコメントを抽出して翻訳
- 📄 **Markdown対応**: コードブロックを保持しながらドキュメント全体を翻訳
- ⚡ **バッチ翻訳**: 高速なバッチ処理による効率的な翻訳
- 🔧 **柔軟な設定**: CLI引数、設定ファイル、または環境変数

## インストール

```bash
pip install repo-translate
```

## クイックスタート

```bash
# 日本語に翻訳
repo-translate karpathy/nanoGPT --lang ja

# 中国語に翻訳（デフォルト）
repo-translate karpathy/nanoGPT

# Zhipu AIを使用
repo-translate karpathy/nanoGPT --provider zhipu --api-key your-api-key

# DeepSeekを使用
repo-translate karpathy/nanoGPT --provider deepseek --api-key sk-xxx
```

## 使用方法

### 基本的な翻訳

```bash
# リポジトリの短縮形
repo-translate owner/repo

# 完全なURL
repo-translate https://github.com/owner/repo

# ターゲット言語を指定
repo-translate owner/repo --lang ko
```

### LLMプロバイダー

```bash
# OpenAI（デフォルト）
repo-translate owner/repo --provider openai --api-key sk-xxx

# DeepSeek
repo-translate owner/repo --provider deepseek --api-key sk-xxx

# Zhipu AI
repo-translate owner/repo --provider zhipu --api-key xxx.xxx

# Moonshot
repo-translate owner/repo --provider moonshot --api-key sk-xxx

# Qwen
repo-translate owner/repo --provider qwen --api-key sk-xxx

# Ollama（ローカル）
repo-translate owner/repo --provider ollama --model llama3

# カスタムOpenAI互換API
repo-translate owner/repo --provider custom --base-url https://api.example.com/v1 --api-key xxx
```

### 設定

`.repo-translate.json`ファイルを作成：

```bash
repo-translate config init
```

設定例：

```json
{
  "provider": "zhipu",
  "model": "glm-4-flash",
  "target_lang": "ja",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "api_key": "your-api-key",
  "batch_size": 5
}
```

**設定の優先順位**（高い順）:

1. CLI引数
2. プロジェクト設定ファイル（`.repo-translate.json`）
3. グローバル設定（`~/.local/share/repo_translate/config.json`）
4. 環境変数
5. デフォルト値

## サポートされているプロバイダー

| プロバイダー | デフォルトモデル | ベースURL |
|-------------|----------------|-----------|
| `openai` | gpt-4o-mini | api.openai.com/v1 |
| `deepseek` | deepseek-chat | api.deepseek.com/v1 |
| `zhipu` | glm-4-flash | open.bigmodel.cn/api/paas/v4 |
| `moonshot` | moonshot-v1-8k | api.moonshot.cn/v1 |
| `qwen` | qwen-turbo | dashscope.aliyuncs.com/compatible-mode/v1 |
| `ollama` | llama3 | localhost:11434/v1 |
| `custom` | gpt-4o-mini | （ユーザー指定） |

## サポートされている言語

| コード | 言語 | コード | 言語 |
|-------|------|-------|------|
| `ja` | 日本語 | `zh` | 中国語 |
| `en` | 英語 | `ko` | 韓国語 |
| `fr` | フランス語 | `de` | ドイツ語 |
| `es` | スペイン語 | `pt` | ポルトガル語 |
| `ru` | ロシア語 | `it` | イタリア語 |
| `ar` | アラビア語 | `th` | タイ語 |
| `vi` | ベトナム語 | `id` | インドネシア語 |

## サポートされているファイルタイプ

| タイプ | 拡張子 | 翻訳内容 |
|--------|--------|----------|
| Markdown | `.md`, `.markdown` | ドキュメント全体（コードブロック保持） |
| Python | `.py`, `.pyw` | コメント、docstring |
| JavaScript | `.js`, `.jsx`, `.mjs` | コメント、JSDoc |
| TypeScript | `.ts`, `.tsx` | コメント、JSDoc |
| C/C++ | `.c`, `.h`, `.cpp`, `.hpp` | コメント、Doxygen |
| Rust | `.rs` | コメント、ドキュメントコメント（`///`、`//!`） |
| Swift | `.swift` | コメント、ドキュメント |

## 出力

翻訳完了後：

```
./repo_name/           # オリジナルのクローンリポジトリ
./repo_name_translated/  # 翻訳されたリポジトリ
```

## 要件

- Python 3.10+
- 選択したLLMプロバイダーのAPIキー

## ライセンス

MITライセンス - 詳細は[LICENSE](LICENSE)を参照してください。

## 貢献

貢献を歓迎します！お気軽にPull Requestを提出してください。

## 謝辞

- [Typer](https://typer.tiangolo.com/)によるCLI構築
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/)によるコード解析
- 様々なLLMプロバイダーによる支援
