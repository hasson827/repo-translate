"""Parser module for extracting translatable content from various file types."""

from .base import Comment, TextBlock, Parser, ParseResult
from .markdown import MarkdownParser
from .python import PythonParser
from .javascript import JavaScriptParser
from .typescript import TypeScriptParser
from .c_cpp import CCppParser
from .rust import RustParser
from .swift import SwiftParser

__all__ = [
    "Comment",
    "TextBlock",
    "Parser",
    "ParseResult",
    "MarkdownParser",
    "PythonParser",
    "JavaScriptParser",
    "TypeScriptParser",
    "CCppParser",
    "RustParser",
    "SwiftParser",
    "get_parser",
]

_PARSERS = {
    "markdown": MarkdownParser,
    "python": PythonParser,
    "javascript": JavaScriptParser,
    "typescript": TypeScriptParser,
    "c": CCppParser,
    "cpp": CCppParser,
    "rust": RustParser,
    "swift": SwiftParser,
}


def get_parser(file_type: str) -> Parser:
    if file_type not in _PARSERS:
        raise ValueError(f"Unsupported file type: {file_type}")
    return _PARSERS[file_type]()
