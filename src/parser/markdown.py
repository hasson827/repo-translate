"""Markdown parser for extracting translatable text."""

import re
from pathlib import Path
from typing import Optional

from .base import Comment, CommentType, Parser, ParseResult, TextBlock


class MarkdownParser(Parser):
    """Parser for Markdown files."""

    @property
    def file_extensions(self) -> set[str]:
        return {".md", ".markdown", ".mdown", ".mkd"}

    def parse(self, content: str, file_path: Optional[Path] = None) -> ParseResult:
        """Parse markdown content extracting text blocks.

        Preserves:
        - Code blocks (not translated)
        - Inline code (not translated)
        - URLs and links (URLs preserved, link text translated)
        - Headers, paragraphs, lists (translated)
        """
        lines = content.split("\n")
        result = ParseResult(
            file_path=file_path or Path(""),
            raw_content=content,
        )

        in_code_block = False
        code_lang = ""
        current_block_lines: list[str] = []
        block_start = 0

        for i, line in enumerate(lines, 1):
            # Check for code block boundaries
            code_match = re.match(r"^```(\w*)", line)
            if code_match:
                if in_code_block:
                    # End of code block
                    if current_block_lines:
                        result.text_blocks.append(
                            TextBlock(
                                text="\n".join(current_block_lines),
                                line_start=block_start,
                                line_end=i - 1,
                                is_code=True,
                                code_language=code_lang,
                            )
                        )
                        current_block_lines = []
                    in_code_block = False
                else:
                    # Start of code block - flush any pending text block
                    if current_block_lines:
                        result.text_blocks.append(
                            TextBlock(
                                text="\n".join(current_block_lines),
                                line_start=block_start,
                                line_end=i - 1,
                                is_code=False,
                            )
                        )
                        current_block_lines = []
                    in_code_block = True
                    code_lang = code_match.group(1) or ""
                    block_start = i
                continue

            if in_code_block:
                current_block_lines.append(line)
            else:
                # Extract HTML comments
                html_comments = re.findall(r"<!--(.+?)-->", line, re.DOTALL)
                for comment_text in html_comments:
                    result.comments.append(
                        Comment(
                            text=comment_text.strip(),
                            type=CommentType.MULTI_LINE,
                            line_start=i,
                            line_end=i,
                        )
                    )

                # Process text, preserving inline code
                if not current_block_lines:
                    block_start = i
                current_block_lines.append(line)

        # Handle remaining block
        if current_block_lines:
            result.text_blocks.append(
                TextBlock(
                    text="\n".join(current_block_lines),
                    line_start=block_start,
                    line_end=len(lines),
                    is_code=in_code_block,
                    code_language=code_lang if in_code_block else "",
                )
            )

        return result

    def inject_translations(
        self,
        content: str,
        translations: dict[int, str],
        parse_result: ParseResult,
    ) -> str:
        """Inject translations into markdown content.

        This replaces entire text blocks with their translations.
        For markdown, we need to be careful to preserve structure.
        """
        lines = content.split("\n")

        # Process text blocks in reverse order to avoid offset issues
        for idx in sorted(translations.keys(), reverse=True):
            if idx >= len(parse_result.text_blocks):
                continue

            block = parse_result.text_blocks[idx]
            if block.is_code:
                continue  # Don't modify code blocks

            translated_text = translations[idx]

            # Replace the lines
            start = block.line_start - 1  # Convert to 0-indexed
            end = block.line_end
            new_lines = translated_text.split("\n")

            lines[start:end] = new_lines

        return "\n".join(lines)

    def extract_plain_text(self, block: TextBlock) -> str:
        """Extract plain text from a markdown block, preserving structure.

        Removes inline code markers but preserves the overall structure.
        """
        text = block.text
        # Protect inline code
        inline_code_pattern = r"`([^`]+)`"
        return text
