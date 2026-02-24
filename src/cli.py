"""Main CLI entry point for repo-translate."""

import tempfile
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table

from .auth import (
    PROVIDER_NAMES,
    get_provider_config,
    list_providers,
    remove,
    set_auth,
    AuthInfo,
    AuthType,
)
from .config import (
    create_project_config,
    load_config,
    save_global_config,
    show_config_sources,
    GLOBAL_CONFIG_FILE,
)
from .parser import get_parser
from .repo import (
    clone_repo,
    filter_translatable_files,
    get_file_list,
    parse_github_url,
)
from .translator import OpenAITranslator
from .translator.openai import PROVIDER_BASE_URLS, PROVIDER_MODELS

app = typer.Typer(
    name="repo-translate",
    help="Translate GitHub repository documentation and code comments",
)
console = Console()

SUPPORTED_LANGUAGES = {
    "zh": "Chinese (中文)",
    "en": "English",
    "ja": "Japanese (日本語)",
    "ko": "Korean (한국어)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "es": "Spanish (Español)",
    "pt": "Portuguese (Português)",
    "ru": "Russian (Русский)",
    "it": "Italian (Italiano)",
    "ar": "Arabic (العربية)",
}


@app.command()
def translate(
    repo_url: str = typer.Argument(..., help="GitHub repository URL or owner/repo"),
    target_lang: Optional[str] = typer.Option(
        None, "--lang", "-l", help="Target language code (default: zh)"
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="LLM provider: openai, deepseek, zhipu, moonshot, qwen, ollama, custom",
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="API key (or set via config/env)"
    ),
    base_url: Optional[str] = typer.Option(
        None, "--base-url", "-u", help="API base URL (for custom providers)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model name (overrides provider default)"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory (default: temp/repo_translated)"
    ),
    dry_run: Optional[bool] = typer.Option(
        None, "--dry-run", help="Show what would be translated without making changes"
    ),
    show_config: bool = typer.Option(
        False, "--show-config", help="Show configuration sources and exit"
    ),
):
    cli_args = {}
    if target_lang:
        cli_args["target_lang"] = target_lang
    if provider:
        cli_args["provider"] = provider
    if api_key:
        cli_args["api_key"] = api_key
    if base_url:
        cli_args["base_url"] = base_url
    if model:
        cli_args["model"] = model
    if dry_run is not None:
        cli_args["dry_run"] = dry_run

    config = load_config(cli_args=cli_args)

    if show_config:
        show_config_sources(config)
        return

    if config.target_lang not in SUPPORTED_LANGUAGES:
        console.print(f"[red]Error:[/red] Unsupported language: {config.target_lang}")
        console.print(f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}")
        raise typer.Exit(1)

    if not config.api_key and config.provider != "ollama":
        provider_name = PROVIDER_NAMES.get(config.provider, config.provider)
        console.print(f"[red]Error:[/red] API key required for {provider_name}")
        console.print(f"Set via --api-key, config file, or REPO_TRANSLATE_API_KEY env")
        raise typer.Exit(1)

    translator = OpenAITranslator(
        api_key=config.api_key or "ollama",
        base_url=config.base_url,
        model=config.model,
        provider=config.provider,
    )

    provider_name = PROVIDER_NAMES.get(config.provider, config.provider)
    console.print(f"\n[bold cyan]repo-translate[/bold cyan]")
    console.print(f"Repository: {repo_url}")
    console.print(f"Provider: {provider_name}")
    if config.model:
        console.print(f"Model: {config.model}")
    console.print(f"Target language: {SUPPORTED_LANGUAGES[config.target_lang]}")
    console.print()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        clone_task = progress.add_task("Cloning repository...", total=None)
        _, repo_name = parse_github_url(repo_url)
        source_path = clone_repo(repo_url, target_dir=Path.cwd() / repo_name)
        progress.remove_task(clone_task)

        scan_task = progress.add_task("Scanning files...", total=None)
        all_files = get_file_list(source_path)
        file_groups = filter_translatable_files(all_files)
        progress.remove_task(scan_task)

    total_files = sum(len(files) for files in file_groups.values())
    console.print(f"[green]✓[/green] Found {total_files} translatable files")
    for file_type, files in file_groups.items():
        console.print(f"  • {file_type}: {len(files)} files")

    if config.dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made[/yellow]")
        console.print("\n[bold]Files to translate:[/bold]")
        for file_type, files in file_groups.items():
            console.print(f"\n{file_type}:")
            for f in files[:10]:
                console.print(f"  {f}")
            if len(files) > 10:
                console.print(f"  ... and {len(files) - 10} more")
        raise typer.Exit(0)

    if output_dir:
        target_path = Path(output_dir)
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path = Path.cwd() / f"{source_path.name}_translated"

    if target_path.exists():
        import shutil

        shutil.rmtree(target_path)
    import shutil

    shutil.copytree(source_path, target_path)

    console.print(f"\n[cyan]→[/cyan] Translating to {target_path}...")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        main_task = progress.add_task("Translating...", total=total_files)

        for file_type, files in file_groups.items():
            parser = get_parser(file_type)

            for file_path in files:
                target_file = target_path / file_path

                progress.update(main_task, description=f"Translating {file_path}")

                content = parser.read_file(target_file)
                parse_result = parser.parse(content, target_file)

                comments_to_translate = {i: c.text for i, c in enumerate(parse_result.comments)}
                blocks_to_translate = {i: b.text for i, b in enumerate(parse_result.text_blocks) if not b.is_code}
                if comments_to_translate:
                    translated_comments = translator.translate_file_comments(
                        list(comments_to_translate.values()), config.target_lang, file_type
                    )
                    comment_map = dict(zip(comments_to_translate.keys(), translated_comments))
                    content = parser.inject_translations(content, comment_map, parse_result)
                if blocks_to_translate:
                    translated_blocks = translator.translate_markdown_blocks(
                        list(blocks_to_translate.values()), config.target_lang
                    )
                    block_map = dict(zip(blocks_to_translate.keys(), translated_blocks))
                    content = parser.inject_translations(content, block_map, parse_result)

                parser.write_file(target_file, content)
                progress.advance(main_task)

    console.print(f"\n[green]✓[/green] Translation complete!")
    console.print(f"Translated files saved to: {target_path}")


config_app = typer.Typer(help="Configuration management")
app.add_typer(config_app, name="config")


@config_app.callback(invoke_without_command=True)
def config_main(
    ctx: typer.Context,
    list_all: bool = typer.Option(False, "--list", "-l", help="List all stored configs"),
    show_sources: bool = typer.Option(False, "--show-sources", help="Show config sources"),
):
    if ctx.invoked_subcommand is not None:
        return

    if show_sources:
        config = load_config()
        show_config_sources(config)
        return

    if list_all:
        providers = list_providers()
        if not providers:
            console.print("[yellow]No provider configurations stored[/yellow]")
            console.print(f"\nConfig file location: {GLOBAL_CONFIG_FILE}")
        else:
            table = Table(title="Stored Provider Configurations")
            table.add_column("Provider")
            table.add_column("API Key")
            table.add_column("Base URL")
            table.add_column("Model")
            for p in providers:
                cfg = get_provider_config(p)
                key = "✓" if cfg.get("api_key") else "✗"
                url = cfg.get("base_url", "-") or "-"
                mdl = cfg.get("model", "-") or "-"
                display = PROVIDER_NAMES.get(p, p)
                table.add_row(display, key, url[:30] + "..." if len(url) > 30 else url, mdl)
            console.print(table)
        return

    console.print(ctx.get_help())


@config_app.command("set")
def config_set(
    provider: str = typer.Argument(
        "openai",
        help="Provider name: openai, deepseek, zhipu, moonshot, qwen, ollama, custom",
    ),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Set API key"),
    base_url: Optional[str] = typer.Option(None, "--base-url", "-u", help="Set base URL"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Set default model"),
    target_lang: Optional[str] = typer.Option(
        None, "--lang", "-l", help="Set default target language"
    ),
    global_config: bool = typer.Option(
        True, "--global/--project", help="Save to global or project config"
    ),
):
    import json

    display_name = PROVIDER_NAMES.get(provider, provider)

    config_data = {}
    if global_config and GLOBAL_CONFIG_FILE.exists():
        try:
            with open(GLOBAL_CONFIG_FILE) as f:
                config_data = json.load(f)
        except Exception:
            pass

    if api_key:
        config_data["api_key"] = api_key
    if base_url:
        config_data["base_url"] = base_url
    if model:
        config_data["model"] = model
    if provider != "global":
        config_data["provider"] = provider
    if target_lang:
        config_data["target_lang"] = target_lang

    if global_config:
        save_global_config(config_data)
    else:
        create_project_config()
        console.print(
            "[yellow]Note:[/yellow] Project config created. Edit .repo-translate.json to add your values."
        )

    console.print(f"[green]✓[/green] Configuration updated for {display_name}")


@config_app.command("init")
def config_init(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path for config file (default: current directory)"
    ),
):
    create_project_config(path)
    console.print("\n[bold]Configuration file created![/bold]")
    console.print("Edit the file to set your preferences:")
    console.print("  • [cyan]provider[/cyan]: LLM provider (openai, deepseek, zhipu, etc.)")
    console.print("  • [cyan]api_key[/cyan]: Your API key")
    console.print("  • [cyan]base_url[/cyan]: Custom API endpoint")
    console.print("  • [cyan]model[/cyan]: Model name")
    console.print("  • [cyan]target_lang[/cyan]: Default target language")


@config_app.command("show")
def config_show():
    config = load_config()
    show_config_sources(config)


@config_app.command("remove")
def config_remove(
    provider: str = typer.Argument(..., help="Provider to remove"),
):
    remove(provider)


@config_app.command("path")
def config_path():
    console.print("\n[bold]Configuration File Locations:[/bold]\n")
    console.print(f"  Global config: {GLOBAL_CONFIG_FILE}")
    console.print(f"  Project config: .repo-translate.json (in current or parent directories)")
    console.print()


@app.command("providers")
def list_providers_cmd():
    console.print("\n[bold]Supported LLM Providers:[/bold]\n")
    for provider, name in PROVIDER_NAMES.items():
        default_url = PROVIDER_BASE_URLS.get(provider, "-")
        default_model = PROVIDER_MODELS.get(provider, "-")
        console.print(f"  [cyan]{provider}[/cyan]: {name}")
        if default_url and provider != "custom":
            console.print(f"    URL: {default_url}")
        console.print(f"    Default model: {default_model}")
        console.print()


@app.command()
def languages():
    console.print("\n[bold]Supported Target Languages:[/bold]\n")
    for code, name in SUPPORTED_LANGUAGES.items():
        default = " (default)" if code == "zh" else ""
        console.print(f"  [cyan]{code}[/cyan]: {name}{default}")
    console.print()


@app.command()
def version():
    from . import __version__

    console.print(f"repo-translate version {__version__}")


if __name__ == "__main__":
    app()
