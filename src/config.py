"""Configuration management for repo-translate.

Supports layered configuration with the following priority (highest to lowest):
1. CLI arguments
2. Project config file (.repo-translate.json or repo_translate.json)
3. Global user config (~/.local/share/repo_translate/config.json)
4. Environment variables
5. Default values
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()

# Config file names to search for (in order)
PROJECT_CONFIG_NAMES = [
    ".repo-translate.json",
    "repo-translate.json",
    ".repo_translate.json",
    "repo_translate.json",
]

# Global config location
GLOBAL_CONFIG_DIR = Path.home() / ".local" / "share" / "repo_translate"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.json"

# Default values
DEFAULTS = {
    "provider": "openai",
    "target_lang": "zh",
    "model": None,
    "base_url": None,
    "api_key": None,
    "github_token": None,
    "push": False,
    "dry_run": False,
    "batch_size": 10,
}


@dataclass
class RepoTranslateConfig:
    """Configuration for repo-translate."""

    provider: str = "openai"
    target_lang: str = "zh"
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    github_token: Optional[str] = None
    push: bool = False
    dry_run: bool = False
    batch_size: int = 10

    # Source tracking (for debugging)
    _source: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "target_lang": self.target_lang,
            "model": self.model,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "github_token": self.github_token,
            "push": self.push,
            "dry_run": self.dry_run,
            "batch_size": self.batch_size,
        }


def _find_project_config(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find project config file by searching current and parent directories.

    Args:
        start_dir: Directory to start search from (default: current directory)

    Returns:
        Path to config file if found, None otherwise
    """
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()

    # Search current directory and parent directories
    while True:
        for name in PROJECT_CONFIG_NAMES:
            config_path = current / name
            if config_path.exists():
                return config_path

        # Stop at home directory or root
        if current == current.parent or current == Path.home():
            break
        current = current.parent

    return None


def _load_json_file(path: Path) -> dict[str, Any]:
    """Load JSON file safely.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON dictionary, or empty dict on error
    """
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        console.print(f"[yellow]![/yellow] Failed to load config {path}: {e}")
        return {}


def _merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple configs, with later ones taking priority.

    None values are skipped, allowing lower-priority configs to shine through.
    """
    result = {}
    for config in configs:
        for key, value in config.items():
            if value is not None:
                result[key] = value
    return result


def load_config(
    project_dir: Optional[Path] = None,
    cli_args: Optional[dict[str, Any]] = None,
) -> RepoTranslateConfig:
    """Load configuration from all sources with proper priority.

    Priority (highest to lowest):
    1. CLI arguments
    2. Project config file
    3. Global user config
    4. Environment variables
    5. Default values

    Args:
        project_dir: Directory to search for project config
        cli_args: CLI arguments (highest priority)

    Returns:
        Merged RepoTranslateConfig
    """
    import os

    # 1. Default values
    defaults = DEFAULTS.copy()

    # 2. Environment variables
    env_config = {
        "api_key": os.environ.get("REPO_TRANSLATE_API_KEY"),
        "provider": os.environ.get("REPO_TRANSLATE_PROVIDER"),
        "model": os.environ.get("REPO_TRANSLATE_MODEL"),
        "base_url": os.environ.get("REPO_TRANSLATE_BASE_URL"),
        "target_lang": os.environ.get("REPO_TRANSLATE_LANG"),
        "github_token": os.environ.get("REPO_TRANSLATE_GITHUB_TOKEN"),
    }
    env_config = {k: v for k, v in env_config.items() if v is not None}

    # 3. Global user config
    global_config = _load_json_file(GLOBAL_CONFIG_FILE)

    # 4. Project config file
    project_config_path = _find_project_config(project_dir)
    project_config = {}
    if project_config_path:
        project_config = _load_json_file(project_config_path)
        console.print(f"[dim]Loaded config from {project_config_path}[/dim]")

    # 5. CLI arguments (filter out None values)
    cli_config = {}
    if cli_args:
        cli_config = {k: v for k, v in cli_args.items() if v is not None}

    # Merge all configs (priority: CLI > project > global > env > defaults)
    merged = _merge_configs(defaults, env_config, global_config, project_config, cli_config)

    # Track sources for debugging
    source = {}
    for key in merged:
        if key in cli_config:
            source[key] = "cli"
        elif key in project_config:
            source[key] = "project"
        elif key in global_config:
            source[key] = "global"
        elif key in env_config:
            source[key] = "env"
        else:
            source[key] = "default"

    config = RepoTranslateConfig(
        provider=merged.get("provider", DEFAULTS["provider"]),
        target_lang=merged.get("target_lang", DEFAULTS["target_lang"]),
        model=merged.get("model"),
        base_url=merged.get("base_url"),
        api_key=merged.get("api_key"),
        github_token=merged.get("github_token"),
        push=merged.get("push", DEFAULTS["push"]),
        dry_run=merged.get("dry_run", DEFAULTS["dry_run"]),
        batch_size=merged.get("batch_size", DEFAULTS["batch_size"]),
        _source=source,
    )

    return config


def save_global_config(config: dict[str, Any]) -> None:
    """Save configuration to global user config file.

    Args:
        config: Configuration dictionary to save
    """
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(GLOBAL_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    console.print(f"[green]✓[/green] Saved global config to {GLOBAL_CONFIG_FILE}")


def create_project_config(path: Optional[Path] = None) -> Path:
    """Create a sample project config file.

    Args:
        path: Path for config file (default: current directory)

    Returns:
        Path to created config file
    """
    if path is None:
        path = Path.cwd() / ".repo-translate.json"

    sample_config = {
        "provider": "openai",
        "target_lang": "zh",
        "model": "gpt-4o-mini",
        "base_url": None,
        "api_key": None,
        "batch_size": 10,
        "_comment": "Remove null values and set your preferences. API key can be set here or via environment variable.",
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample_config, f, indent=2)

    console.print(f"[green]✓[/green] Created config template at {path}")
    return path


def show_config_sources(config: RepoTranslateConfig) -> None:
    """Display where each config value comes from (for debugging)."""
    from rich.table import Table

    table = Table(title="Configuration Sources")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_column("Source")

    for key, value in config.to_dict().items():
        if key.startswith("_"):
            continue
        source = config._source.get(key, "default")
        # Mask sensitive values
        if key in ("api_key", "github_token") and value:
            display_value = "*" * 8 + "..." + str(value)[-4:] if len(str(value)) > 4 else "****"
        else:
            display_value = str(value) if value is not None else "-"
        table.add_row(key, display_value, source)

    console.print(table)
