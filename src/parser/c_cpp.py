"""C/C++ parser using tree-sitter."""

import tree_sitter_c as tsc
from pathlib import Path
from typing import Optional

from tree_sitter import Language, Parser as TSParser

from .base import Comment, CommentType, Parser, ParseResult


class CCppParser(Parser):
    """Parser for C/C++ files using tree-sitter."""

    @property
    def file_extensions(self) -> set[str]:
        return {".c", ".h", ".cpp", ".cxx", ".cc", ".hpp", ".hxx", ".hh"}

    def _get_language(self) -> Language:
        return Language(tsc.language())

    def parse(self, content: str, file_path: Optional[Path] = None) -> ParseResult:
        result = ParseResult(
            file_path=file_path or Path(""),
            raw_content=content,
        )
        try:
            language = self._get_language()
            parser = TSParser(language)
            tree = parser.parse(bytes(content, "utf-8"))
            self._extract_comments(tree.root_node, result)
        except Exception:
            pass
        result.comments.sort(key=lambda c: c.line_start)
        return result

    def _extract_comments(self, node, result: ParseResult) -> None:
        if node.type == "comment":
            comment_text = node.text.decode("utf-8")
            if comment_text.startswith("/**") or comment_text.startswith("/*!"):
                comment_type = CommentType.DOC_COMMENT
            elif comment_text.startswith("///"):
                comment_type = CommentType.DOC_COMMENT
            elif comment_text.startswith("/*"):
                comment_type = CommentType.MULTI_LINE
            else:
                comment_type = CommentType.SINGLE_LINE
            clean_text = self._clean_comment_text(comment_text, comment_type)
            result.comments.append(
                Comment(
                    text=clean_text,
                    type=comment_type,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    column_start=node.start_point[1],
                    column_end=node.end_point[1],
                    original=comment_text,
                )
            )
        for child in node.children:
            self._extract_comments(child, result)

    def _clean_comment_text(self, comment: str, comment_type: CommentType) -> str:
        if comment_type == CommentType.SINGLE_LINE:
            return comment.lstrip("/").strip()
        elif comment_type == CommentType.DOC_COMMENT:
            if comment.startswith("///"):
                return comment.strip("/").strip()
            text = comment.strip("/*").strip("*/").strip()
            lines = []
            for line in text.split("\n"):
                line = line.strip()
                if line.startswith("*"):
                    line = line[1:].strip()
                lines.append(line)
            return "\n".join(lines).strip()
        elif comment_type == CommentType.MULTI_LINE:
            text = comment.strip("/*").strip("*/").strip()
            lines = []
            for line in text.split("\n"):
                line = line.strip()
                if line.startswith("*"):
                    line = line[1:].strip()
                lines.append(line)
            return "\n".join(lines).strip()
        return comment

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
                slash_pos = original_line.find("//")
                indent = original_line[:slash_pos]
                lines[start_line] = f"{indent}// {translated}"
            elif comment.type == CommentType.DOC_COMMENT:
                original_first = lines[start_line]
                indent = ""
                for char in original_first:
                    if char in " \t":
                        indent += char
                    else:
                        break
                if comment.original.startswith("///"):
                    trans_lines = translated.split("\n")
                    new_lines = [f"{indent}/// {line}" for line in trans_lines]
                    lines[start_line : end_line + 1] = new_lines
                else:
                    trans_lines = translated.split("\n")
                    if len(trans_lines) == 1:
                        lines[start_line] = f"{indent}/** {translated} */"
                    else:
                        new_lines = [f"{indent}/**"]
                        for trans_line in trans_lines:
                            new_lines.append(f"{indent} * {trans_line}")
                        new_lines.append(f"{indent} */")
                        lines[start_line : end_line + 1] = new_lines
            elif comment.type == CommentType.MULTI_LINE:
                original_first = lines[start_line]
                indent = ""
                for char in original_first:
                    if char in " \t":
                        indent += char
                    else:
                        break
                trans_lines = translated.split("\n")
                if len(trans_lines) == 1:
                    lines[start_line] = f"{indent}/* {translated} */"
                else:
                    new_lines = [f"{indent}/*"]
                    for trans_line in trans_lines:
                        new_lines.append(f"{indent}   {trans_line}")
                    new_lines.append(f"{indent} */")
                    lines[start_line : end_line + 1] = new_lines
        return "\n".join(lines)
