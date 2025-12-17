import click


@click.command()
def research():
    """
    Research the given topic and return the results.
    """
    click.echo("Researching the given topic...")
