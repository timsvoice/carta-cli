from carta.commands import discover
import click


@click.group()
def cli():
    """
    Carta CLI
    """
    pass


cli.add_command(discover.discover_gather)
