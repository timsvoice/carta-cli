from carta.commands import research
import click


@click.group()
def cli():
    """
    Carta CLI
    """
    pass


cli.add_command(research.research)
