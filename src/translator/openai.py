"""OpenAI-compatible translator for batch text translation.

Supports OpenAI, DeepSeek, Zhipu (智谱), and any OpenAI-compatible API.
"""

from typing import Optional

from openai import OpenAI
from rich.console import Console
from tenacity import retry, stop_after_attempt, wait_exponential

console = Console()

LANGUAGE_NAMES = {
    "zh": "Chinese",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
    "ar": "Arabic",
    "hi": "Hindi",
}

# Popular OpenAI-compatible providers
PROVIDER_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "moonshot": "https://api.moonshot.cn/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "ollama": "http://localhost:11434/v1",
    "custom": None,  # User-provided URL
}

# Default models for each provider
PROVIDER_MODELS = {
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "zhipu": "glm-4-flash",
    "moonshot": "moonshot-v1-8k",
    "qwen": "qwen-turbo",
    "ollama": "llama3",
    "custom": "gpt-4o-mini",
}


class OpenAITranslator:
    """Translator using OpenAI-compatible API.

    Supports OpenAI, DeepSeek, Zhipu, Moonshot, Qwen, Ollama, and any
    OpenAI-compatible API endpoint.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        provider: str = "openai",
    ):
        """Initialize the translator.

        Args:
            api_key: API key for the provider
            base_url: Custom base URL (overrides provider default)
            model: Model to use (overrides provider default)
            provider: Provider name for default settings
        """
        # Resolve base_url
        if base_url:
            self.base_url = base_url
        elif provider in PROVIDER_BASE_URLS:
            self.base_url = PROVIDER_BASE_URLS[provider]
        else:
            self.base_url = PROVIDER_BASE_URLS["openai"]

        # Resolve model
        if model:
            self.model = model
        elif provider in PROVIDER_MODELS:
            self.model = PROVIDER_MODELS[provider]
        else:
            self.model = PROVIDER_MODELS["openai"]

        # Initialize client
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.base_url,
        )
        self.provider = provider

    def _get_language_name(self, lang_code: str) -> str:
        return LANGUAGE_NAMES.get(lang_code, lang_code)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
    )
    def translate_batch(
        self,
        texts: list[str],
        target_lang: str = "zh",
        source_lang: str = "en",
        context: str = "",
    ) -> list[str]:
        if not texts:
            return []

        target_name = self._get_language_name(target_lang)
        source_name = self._get_language_name(source_lang)

        system_prompt = f"""You are a professional translator specializing in technical documentation and code comments.
Translate the following texts from {source_name} to {target_name}.

Rules:
1. Preserve all code syntax, variable names, and technical terms
2. Keep markdown formatting intact (headers, links, code blocks, etc.)
3. Maintain the original tone and style
4. For code comments, keep them concise and clear
5. Do not translate URLs, file paths, or command-line examples
6. Preserve placeholder variables like {{name}}, %s, {{0}}, etc.
7. Return ONLY the translated text, nothing else"""

        if context:
            system_prompt += f"\n\nContext: {context}"

        user_prompt = "Translate the following texts. Each item is separated by '---SEPARATOR---'. Return translations in the same order with the same separator.\n\n"
        user_prompt += "\n\n---SEPARATOR---\n\n".join(texts)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=4096,
            )

            translated = response.choices[0].message.content or ""
            results = translated.split("---SEPARATOR---")

            results = [r.strip() for r in results]

            if len(results) != len(texts):
                console.print(
                    f"[yellow]![/yellow] Translation count mismatch: {len(results)} vs {len(texts)}, using fallback"
                )
                return self._translate_one_by_one(texts, target_lang, source_lang)

            return results

        except Exception as e:
            console.print(f"[red]✗[/red] Batch translation failed: {e}")
            return self._translate_one_by_one(texts, target_lang, source_lang)

    def _translate_one_by_one(
        self,
        texts: list[str],
        target_lang: str,
        source_lang: str,
    ) -> list[str]:
        results = []
        target_name = self._get_language_name(target_lang)
        source_name = self._get_language_name(source_lang)

        for text in texts:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"Translate from {source_name} to {target_name}. Preserve code syntax, markdown formatting, and technical terms. Return ONLY the translation.",
                        },
                        {"role": "user", "content": text},
                    ],
                    temperature=0.3,
                )
                results.append(response.choices[0].message.content or text)
            except Exception:
                results.append(text)

        return results

    def translate_file_comments(
        self,
        comments: list[str],
        target_lang: str = "zh",
        file_type: str = "",
        batch_size: int = 10,
    ) -> list[str]:
        results = []

        for i in range(0, len(comments), batch_size):
            batch = comments[i : i + batch_size]
            context = f"This is from a {file_type} file." if file_type else ""
            translated = self.translate_batch(batch, target_lang, context=context)
            results.extend(translated)

        return results

    def translate_markdown_blocks(
        self,
        blocks: list[str],
        target_lang: str = "zh",
        batch_size: int = 3,
    ) -> list[str]:
        results = []

        for i in range(0, len(blocks), batch_size):
            batch = blocks[i : i + batch_size]
            translated = self.translate_batch(
                batch, target_lang, context="This is markdown documentation."
            )
            results.extend(translated)

        return results
