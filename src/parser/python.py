"""Python parser using ast-comments to preserve comments."""

import ast
from pathlib import Path
from typing import Optional

try:
    import ast_comments as astc

    HAS_AST_COMMENTS = True
except ImportError:
    HAS_AST_COMMENTS = False
    astc = None

from .base import Comment, CommentType, Parser, ParseResult


class _CommentNode:
    """Helper to detect Comment nodes from ast-comments."""

    pass


if HAS_AST_COMMENTS and hasattr(astc, "Comment"):
    _CommentNode = astc.Comment


class PythonParser(Parser):
    """Parser for Python files using ast-comments."""

    @property
    def file_extensions(self) -> set[str]:
        return {".py", ".pyw"}

    def parse(self, content: str, file_path: Optional[Path] = None) -> ParseResult:
        result = ParseResult(
            file_path=file_path or Path(""),
            raw_content=content,
        )

        if not HAS_AST_COMMENTS:
            return self._parse_standard(content, result)

        try:
            tree = astc.parse(content)
        except SyntaxError:
            return result

        lines = content.split("\n")

        # New API: Comment nodes are in the AST tree
        for node in ast.walk(tree):
            # Handle Comment nodes from ast-comments
            if HAS_AST_COMMENTS and isinstance(node, _CommentNode):
                comment_text = node.value if hasattr(node, "value") else str(node)
                lineno = getattr(node, "lineno", 1)
                col_offset = getattr(node, "col_offset", 0)

                # Determine if it's inline (after code) or standalone
                if col_offset > 0:
                    comment_type = CommentType.SINGLE_LINE  # inline
                else:
                    comment_type = CommentType.SINGLE_LINE

                result.comments.append(
                    Comment(
                        text=comment_text.lstrip("#").strip(),
                        type=comment_type,
                        line_start=lineno,
                        line_end=lineno,
                        column_start=col_offset,
                        column_end=col_offset + len(comment_text),
                        original=comment_text,
                    )
                )

        # Also extract docstrings
        for node in ast.walk(tree):
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
            ):
                continue
            docstring = ast.get_docstring(node)
            if not docstring:
                continue
            if node.body and isinstance(node.body[0], ast.Expr):
                if isinstance(node.body[0].value, ast.Constant):
                    doc_node = node.body[0].value
                    quote_style = self._detect_quote_style(content, docstring)
                    result.comments.append(
                        Comment(
                            text=docstring,
                            type=CommentType.DOCSTRING,
                            line_start=doc_node.lineno,
                            line_end=getattr(doc_node, "end_lineno", doc_node.lineno)
                            or doc_node.lineno,
                            column_start=doc_node.col_offset,
                            column_end=getattr(doc_node, "end_col_offset", 0) or 0,
                            original=quote_style + docstring + quote_style,
                        )
                    )

        result.comments.sort(key=lambda c: c.line_start)
        return result

    def _detect_quote_style(self, content: str, docstring: str) -> str:
        pos = content.find(docstring)
        if pos <= 0:
            return '"""'
        before = content[max(0, pos - 10) : pos]
        if '"""' in before:
            return '"""'
        return "'''"

    def _parse_standard(self, content: str, result: ParseResult) -> ParseResult:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return result

        for node in ast.walk(tree):
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
            ):
                continue
            docstring = ast.get_docstring(node)
            if not docstring:
                continue
            if node.body and isinstance(node.body[0], ast.Expr):
                doc_node = node.body[0].value
                result.comments.append(
                    Comment(
                        text=docstring,
                        type=CommentType.DOCSTRING,
                        line_start=doc_node.lineno,
                        line_end=getattr(doc_node, "end_lineno", doc_node.lineno)
                        or doc_node.lineno,
                    )
                )
        return result

    def inject_translations(
        self,
        content: str,
        translations: dict[int, str],
        parse_result: ParseResult,
    ) -> str:
        lines = content.split("\n")

        for idx in sorted(translations.keys(), reverse=True):
            if idx >= len(parse_result.comments):
                continue

            comment = parse_result.comments[idx]
            translated = translations[idx]

            start_line = comment.line_start - 1
            end_line = comment.line_end - 1

            if comment.type == CommentType.SINGLE_LINE:
                original_line = lines[start_line]
                hash_pos = original_line.find("#")
                if hash_pos == -1:
                    continue
                indent = original_line[: hash_pos + 1]
                lines[start_line] = f"{indent} {translated}"

            elif comment.type == CommentType.DOCSTRING:
                quote = '"""' if '"""' in comment.original else "'''"

                if start_line == end_line:
                    indent = ""
                    for char in lines[start_line]:
                        if char in " \t":
                            indent += char
                        else:
                            break
                    lines[start_line] = f"{indent}{quote}{translated}{quote}"
                else:
                    original_first = lines[start_line]
                    indent = ""
                    for char in original_first:
                        if char in " \t":
                            indent += char
                        else:
                            break

                    new_lines = [f"{indent}{quote}"]
                    for trans_line in translated.split("\n"):
                        new_lines.append(f"{indent}    {trans_line}")
                    new_lines.append(f"{indent}{quote}")

                    lines[start_line : end_line + 1] = new_lines

            elif comment.type == CommentType.MULTI_LINE:
                translated_lines = translated.split("\n")
                lines[start_line : end_line + 1] = translated_lines

        return "\n".join(lines)
