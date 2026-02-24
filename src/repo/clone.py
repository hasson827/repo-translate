"""Repository cloning and file scanning operations."""

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from git import Repo
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# File patterns to skip
SKIP_PATTERNS = [
    # Directories
    r"^node_modules/",
    r"^\.git/",
    r"^__pycache__/",
    r"^\.venv/",
    r"^venv/",
    r"^\.tox/",
    r"^\.pytest_cache/",
    r"^\.mypy_cache/",
    r"^dist/",
    r"^build/",
    r"^\.eggs/",
    r"^\.idea/",
    r"^\.vscode/",
    r"^target/",  # Rust
    r"^Pods/",  # iOS
    # Files
    r"\.lock$",
    r"\.sum$",
    r"-lock\.json$",
    r"\.pyc$",
    r"\.pyo$",
    r"\.so$",
    r"\.dylib$",
    r"\.dll$",
    r"\.exe$",
    r"\.bin$",
    r"\.png$",
    r"\.jpg$",
    r"\.jpeg$",
    r"\.gif$",
    r"\.ico$",
    r"\.svg$",
    r"\.woff2?$",
    r"\.ttf$",
    r"\.eot$",
    r"\.mp[34]$",
    r"\.wav$",
    r"\.pdf$",
    r"\.zip$",
    r"\.tar\.gz$",
    r"\.rar$",
]

# Translatable file extensions by type
TRANSLATABLE_EXTENSIONS = {
    "markdown": {".md", ".markdown", ".mdown", ".mkd"},
    "python": {".py", ".pyw"},
    "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx", ".mts", ".cts"},
    "c": {".c", ".h"},
    "cpp": {".cpp", ".cxx", ".cc", ".hpp", ".hxx", ".hh"},
    "rust": {".rs"},
    "swift": {".swift"},
    "text": {".txt", ".rst", ".adoc"},
}


def parse_github_url(url: str) -> tuple[str, str]:
    """Parse GitHub URL to extract owner and repo name.

    Args:
        url: GitHub URL (https://github.com/owner/repo or owner/repo)

    Returns:
        Tuple of (owner, repo_name)
    """
    # Handle shorthand format (owner/repo)
    if "/" in url and not url.startswith("http"):
        parts = url.split("/")
        return parts[0], parts[1].replace(".git", "")

    # Handle full URL
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")

    if len(parts) >= 2:
        return parts[0], parts[1].replace(".git", "")

    raise ValueError(f"Invalid GitHub URL: {url}")


def clone_repo(
    repo_url: str,
    target_dir: Optional[Path] = None,
    progress: Optional[Progress] = None,
) -> Path:
    """Clone a GitHub repository.

    Args:
        repo_url: GitHub repository URL or owner/repo shorthand
        target_dir: Directory to clone into (default: temp directory)
        progress: Rich progress instance for UI

    Returns:
        Path to cloned repository
    """
    owner, repo_name = parse_github_url(repo_url)

    # Construct full URL if needed
    if not repo_url.startswith("http"):
        repo_url = f"https://github.com/{owner}/{repo_name}.git"

    # Create target directory
    if target_dir is None:
        target_dir = Path(tempfile.mkdtemp()) / f"{repo_name}_source"
    else:
        target_dir = Path(target_dir)

    # Remove if exists
    if target_dir.exists():
        shutil.rmtree(target_dir)

    if progress:
        with progress:
            task = progress.add_task(f"Cloning {owner}/{repo_name}...", total=None)
            Repo.clone_from(repo_url, str(target_dir), depth=1)
            progress.remove_task(task)
    else:
        console.print(f"[cyan]→[/cyan] Cloning {owner}/{repo_name}...")
        Repo.clone_from(repo_url, str(target_dir), depth=1)

    console.print(f"[green]✓[/green] Cloned to {target_dir}")
    return target_dir


def get_file_list(repo_path: Path) -> list[Path]:
    """Get list of all files in repository.

    Args:
        repo_path: Path to cloned repository

    Returns:
        List of file paths (relative to repo root)
    """
    files = []
    for root, _, filenames in os.walk(repo_path):
        root_path = Path(root)
        for filename in filenames:
            file_path = root_path / filename
            rel_path = file_path.relative_to(repo_path)
            files.append(rel_path)
    return sorted(files)


def should_skip(path: Path) -> bool:
    """Check if a file should be skipped.

    Args:
        path: Relative path to file

    Returns:
        True if file should be skipped
    """
    path_str = str(path)
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, path_str):
            return True
    return False


def get_file_type(path: Path) -> Optional[str]:
    """Get the file type for translation purposes.

    Args:
        path: File path

    Returns:
        File type name or None if not translatable
    """
    ext = path.suffix.lower()
    for file_type, extensions in TRANSLATABLE_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return None


def filter_translatable_files(files: list[Path]) -> dict[str, list[Path]]:
    """Filter files and group by translatable type.

    Args:
        files: List of file paths

    Returns:
        Dictionary mapping file type to list of files
    """
    result: dict[str, list[Path]] = {}

    for file_path in files:
        if should_skip(file_path):
            continue

        file_type = get_file_type(file_path)
        if file_type:
            if file_type not in result:
                result[file_type] = []
            result[file_type].append(file_path)

    return result
