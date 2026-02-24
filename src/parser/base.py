"""Base parser classes and types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class CommentType(Enum):
    """Type of code comment."""

    SINGLE_LINE = "single"  # # comment or // comment
    MULTI_LINE = "multi"  # /* comment */
    DOCSTRING = "docstring"  # Python docstrings
    JSDOC = "jsdoc"  # /** @param ... */
    DOC_COMMENT = "doc"  # /// Rust doc comments


@dataclass
class Comment:
    """Represents a code comment."""

    text: str
    type: CommentType
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    original: str = ""  # Original text including comment markers

    def __post_init__(self):
        if not self.original:
            self.original = self.text


@dataclass
class TextBlock:
    """Represents a block of translatable text (e.g., in markdown)."""

    text: str
    line_start: int
    line_end: int
    is_code: bool = False
    code_language: str = ""
    original: str = ""  # Original text including any formatting

    def __post_init__(self):
        if not self.original:
            self.original = self.text


@dataclass
class ParseResult:
    """Result of parsing a file."""

    file_path: Path
    comments: list[Comment] = field(default_factory=list)
    text_blocks: list[TextBlock] = field(default_factory=list)
    raw_content: str = ""


class Parser(ABC):
    """Abstract base class for file parsers."""

    @property
    @abstractmethod
    def file_extensions(self) -> set[str]:
        """Supported file extensions."""
        pass

    @abstractmethod
    def parse(self, content: str, file_path: Optional[Path] = None) -> ParseResult:
        """Parse file content and extract translatable elements.

        Args:
            content: File content as string
            file_path: Optional file path for context

        Returns:
            ParseResult with extracted comments and text blocks
        """
        pass

    @abstractmethod
    def inject_translations(
        self,
        content: str,
        translations: dict[int, str],
        parse_result: ParseResult,
    ) -> str:
        """Inject translations back into the content.

        Args:
            content: Original file content
            translations: Dictionary mapping element index to translated text
            parse_result: Original parse result with element positions

        Returns:
            Content with translations injected
        """
        pass

    def read_file(self, file_path: Path) -> str:
        """Read file content.

        Args:
            file_path: Path to file

        Returns:
            File content as string
        """
        return file_path.read_text(encoding="utf-8", errors="replace")

    def write_file(self, file_path: Path, content: str) -> None:
        """Write content to file.

        Args:
            file_path: Path to file
            content: Content to write
        """
        file_path.write_text(content, encoding="utf-8")
