from carta.commands import research, cache
import click


@click.group()
def cli():
    """
    Carta CLI
    """
    pass


cli.add_command(research.research)
cli.add_command(cache.cache)
