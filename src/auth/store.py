"""Authentication storage for API keys.

Design inspired by opencode: stores credentials in ~/.local/share/repo_translate/auth.json
with file permissions 0o600 for security.

Supports multiple providers: OpenAI, DeepSeek, Zhipu, Moonshot, Qwen, Ollama, etc.
"""

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()

# Storage location for auth credentials
AUTH_DIR = Path.home() / ".local" / "share" / "repo_translate"
AUTH_FILE = AUTH_DIR / "auth.json"

# Provider display names
PROVIDER_NAMES = {
    "openai": "OpenAI",
    "deepseek": "DeepSeek",
    "zhipu": "智谱 AI (GLM)",
    "moonshot": "Moonshot (月之暗面)",
    "qwen": "通义千问 (Qwen)",
    "ollama": "Ollama (本地)",
    "custom": "自定义 (Custom)",
}


class AuthType(Enum):
    """Supported authentication types."""

    API_KEY = "api"
    OAUTH = "oauth"


@dataclass
class AuthInfo:
    """Authentication information for a provider."""

    type: AuthType
    key: Optional[str] = None
    base_url: Optional[str] = None  # Custom base URL for OpenAI-compatible APIs
    model: Optional[str] = None  # Preferred model for this provider
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    expires_at: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {"type": self.type.value}
        if self.key:
            result["key"] = self.key
        if self.base_url:
            result["base_url"] = self.base_url
        if self.model:
            result["model"] = self.model
        if self.refresh_token:
            result["refresh"] = self.refresh_token
        if self.access_token:
            result["access"] = self.access_token
        if self.expires_at is not None:
            result["expires"] = self.expires_at
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "AuthInfo":
        """Create AuthInfo from dictionary."""
        auth_type = AuthType(data["type"])
        return cls(
            type=auth_type,
            key=data.get("key"),
            base_url=data.get("base_url"),
            model=data.get("model"),
            refresh_token=data.get("refresh"),
            access_token=data.get("access"),
            expires_at=data.get("expires"),
        )


def _ensure_auth_dir() -> None:
    """Ensure auth directory exists with correct permissions."""
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(AUTH_DIR, 0o700)


def _load_auth_data() -> dict:
    """Load all auth data from file."""
    if not AUTH_FILE.exists():
        return {}
    try:
        with open(AUTH_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_auth_data(data: dict) -> None:
    """Save auth data to file with secure permissions."""
    _ensure_auth_dir()
    with open(AUTH_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(AUTH_FILE, 0o600)


def get(provider: str) -> Optional[AuthInfo]:
    """Get authentication info for a provider.

    Args:
        provider: Provider name (e.g., "openai", "deepseek", "zhipu")

    Returns:
        AuthInfo if exists, None otherwise
    """
    data = _load_auth_data()
    if provider in data:
        return AuthInfo.from_dict(data[provider])
    return None


def set_auth(provider: str, info: AuthInfo) -> None:
    """Set authentication info for a provider.

    Args:
        provider: Provider name (e.g., "openai", "deepseek")
        info: Authentication information to store
    """
    data = _load_auth_data()
    data[provider] = info.to_dict()
    _save_auth_data(data)
    display_name = PROVIDER_NAMES.get(provider, provider)
    console.print(f"[green]✓[/green] Configuration for {display_name} saved successfully")


def remove(provider: str) -> bool:
    """Remove authentication for a provider.

    Args:
        provider: Provider name to remove

    Returns:
        True if removed, False if not found
    """
    data = _load_auth_data()
    if provider in data:
        del data[provider]
        _save_auth_data(data)
        display_name = PROVIDER_NAMES.get(provider, provider)
        console.print(f"[green]✓[/green] Configuration for {display_name} removed")
        return True
    display_name = PROVIDER_NAMES.get(provider, provider)
    console.print(f"[yellow]![/yellow] No configuration found for {display_name}")
    return False


def list_providers() -> list[str]:
    """List all providers with stored credentials.

    Returns:
        List of provider names
    """
    data = _load_auth_data()
    return list(data.keys())


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a provider (convenience function).

    Checks environment variable first, then stored credentials.

    Args:
        provider: Provider name

    Returns:
        API key if found, None otherwise
    """
    # Check environment variable first (e.g., OPENAI_API_KEY, DEEPSEEK_API_KEY)
    env_var = f"{provider.upper()}_API_KEY"
    env_key = os.environ.get(env_var)
    if env_key:
        return env_key

    # Check stored credentials
    auth = get(provider)
    if auth and auth.key:
        return auth.key

    return None


def get_provider_config(provider: str) -> dict:
    """Get full provider configuration including base_url and model.

    Args:
        provider: Provider name

    Returns:
        Dictionary with api_key, base_url, model (all optional)
    """
    result = {}

    # Get API key
    api_key = get_api_key(provider)
    if api_key:
        result["api_key"] = api_key

    # Get stored config
    auth = get(provider)
    if auth:
        if auth.base_url:
            result["base_url"] = auth.base_url
        if auth.model:
            result["model"] = auth.model

    return result
