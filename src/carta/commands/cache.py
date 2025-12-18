import click
from pathlib import Path

from carta.utils.cache import build_cache


@click.group()
def cache():
    """Manage codebase cache for LLM context."""
    pass


@cache.command()
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Source directory to analyze (default: current directory)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=".cache",
    help="Output cache directory (default: .cache)",
)
def build(source: Path, output: Path):
    """
    Build a cache of function signatures and module dependencies.

    Parses Python files and extracts structure for LLM context.
    """
    click.echo(f"Building cache for: {source.resolve()}")
    click.echo(f"Output directory: {output.resolve()}")

    cached = build_cache(source, output)

    click.echo(click.style(f"\n✓ Cached {len(cached)} files", fg="green"))
    for path in sorted(cached.keys()):
        click.echo(f"  • {path}")
