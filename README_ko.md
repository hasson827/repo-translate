# repo-translate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**GitHub 저장소 문서와 코드 주석을 원하는 언어로 번역합니다.**

GitHub 저장소를 복제하고 모든 문서(README, docs)와 코드 주석을 대상 언어로 번역하는 강력한 CLI 도구입니다.

[English](README.md) | [中文](README_zh-CN.md) | [繁體中文](README_zh-TW.md) | [日本語](README_ja.md)

## 특징

- 🌍 **다국어 지원**: 10개 이상의 언어로 번역 가능
- 🤖 **다중 프로바이더 지원**: OpenAI, DeepSeek, Zhipu (GLM), Moonshot, Qwen, Ollama 및 모든 OpenAI 호환 API
- 📝 **스마트 파싱**: Python, JavaScript/TypeScript, C/C++, Rust, Swift에서 주석 추출 및 번역
- 📄 **Markdown 지원**: 코드 블록을 보존하면서 전체 문서 번역
- ⚡ **배치 번역**: 효율적인 배치 처리로 빠른 번역
- 🔧 **유연한 설정**: CLI 인수, 설정 파일 또는 환경 변수

## 설치

```bash
pip install repo-translate
```

## 빠른 시작

```bash
# 한국어로 번역
repo-translate translate karpathy/nanoGPT --lang ko

# 중국어로 번역 (기본값)
repo-translate translate karpathy/nanoGPT

# Zhipu AI 사용
repo-translate translate karpathy/nanoGPT --provider zhipu --api-key your-api-key

# DeepSeek 사용
repo-translate translate karpathy/nanoGPT --provider deepseek --api-key sk-xxx
```

## 사용법

### 기본 번역

```bash
# 저장소 약어
repo-translate translate owner/repo

# 전체 URL
repo-translate translate https://github.com/owner/repo

# 대상 언어 지정
repo-translate translate owner/repo --lang ja
```

### LLM 프로바이더

```bash
# OpenAI (기본값)
repo-translate translate owner/repo --provider openai --api-key sk-xxx

# DeepSeek
repo-translate translate owner/repo --provider deepseek --api-key sk-xxx

# Zhipu AI
repo-translate translate owner/repo --provider zhipu --api-key xxx.xxx

# Moonshot
repo-translate translate owner/repo --provider moonshot --api-key sk-xxx

# Qwen
repo-translate translate owner/repo --provider qwen --api-key sk-xxx

# Ollama (로컬)
repo-translate translate owner/repo --provider ollama --model llama3

# 사용자 정의 OpenAI 호환 API
repo-translate translate owner/repo --provider custom --base-url https://api.example.com/v1 --api-key xxx
```

### 설정

`.repo-translate.json` 파일 생성:

```bash
repo-translate config init
```

설정 예시:

```json
{
  "provider": "zhipu",
  "model": "glm-4-flash",
  "target_lang": "ko",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "api_key": "your-api-key",
  "batch_size": 5
}
```

**설정 우선순위** (높은 순):

1. CLI 인수
2. 프로젝트 설정 파일 (`.repo-translate.json`)
3. 전역 설정 (`~/.local/share/repo_translate/config.json`)
4. 환경 변수
5. 기본값

### CLI 명령

```bash
# 설정 파일 초기화
repo-translate config init

# 전역 프로바이더 설정 지정
repo-translate config set zhipu --api-key xxx --model glm-4-flash

# 현재 설정 표시
repo-translate config show

# 지원되는 프로바이더 목록
repo-translate providers

# 지원되는 언어 목록
repo-translate languages

# 드라이런 (미리보기만, 변경 없음)
repo-translate translate owner/repo --dry-run
```

### 환경 변수

```bash
export REPO_TRANSLATE_API_KEY=your-api-key
export REPO_TRANSLATE_PROVIDER=zhipu
export REPO_TRANSLATE_MODEL=glm-4-flash
repo-translate translate owner/repo
```
## 지원 프로바이더

| 프로바이더 | 기본 모델 | 베이스 URL |
|-----------|----------|------------|
| `openai` | gpt-4o-mini | api.openai.com/v1 |
| `deepseek` | deepseek-chat | api.deepseek.com/v1 |
| `zhipu` | glm-4-flash | open.bigmodel.cn/api/paas/v4 |
| `moonshot` | moonshot-v1-8k | api.moonshot.cn/v1 |
| `qwen` | qwen-turbo | dashscope.aliyuncs.com/compatible-mode/v1 |
| `ollama` | llama3 | localhost:11434/v1 |
| `custom` | gpt-4o-mini | (사용자 제공) |

## 지원 언어

| 코드 | 언어 | 코드 | 언어 |
|------|------|------|------|
| `ko` | 한국어 | `zh` | 중국어 |
| `en` | 영어 | `ja` | 일본어 |
| `fr` | 프랑스어 | `de` | 독일어 |
| `es` | 스페인어 | `pt` | 포르투갈어 |
| `ru` | 러시아어 | `it` | 이탈리아어 |
| `ar` | 아랍어 | `th` | 태국어 |
| `vi` | 베트남어 | `id` | 인도네시아어 |

## 지원 파일 형식

| 유형 | 확장자 | 번역 내용 |
|------|--------|----------|
| Markdown | `.md`, `.markdown` | 전체 문서 (코드 블록 보존) |
| Python | `.py`, `.pyw` | 주석, 독스트링 |
| JavaScript | `.js`, `.jsx`, `.mjs` | 주석, JSDoc |
| TypeScript | `.ts`, `.tsx` | 주석, JSDoc |
| C/C++ | `.c`, `.h`, `.cpp`, `.hpp` | 주석, Doxygen |
| Rust | `.rs` | 주석, 문서 주석 (`///`, `//!`) |
| Swift | `.swift` | 주석, 문서 |

## 출력

번역 완료 후:

```
./repo_name/           # 원본 복제 저장소
./repo_name_translated/  # 번역된 저장소
```

## 요구사항

- Python 3.10+
- 선택한 LLM 프로바이더의 API 키

## 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

## 기여

기여를 환영합니다! 자유롭게 Pull Request를 제출해 주세요.

## 감사의 말

- [Typer](https://typer.tiangolo.com/)로 CLI 구축
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/)로 코드 파싱
- 다양한 LLM 프로바이더의 지원
