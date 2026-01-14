import click

from carta.utils.cache import build_cache

"""
The purpose of the Discover module is to gather context from the codebase and develop a high-level design document.

@TODO: Add discover prompt (old spec prompt)
@TODO: Add a module for interacting with the LLM
@TODO: Add a function for performing an agentic tool loop for context gathering
"""


@click.command()
def discover():
    """
    Discover and document requirements for a feature.
    """
    # Build cache of stripped Python files for LLM context
    build_cache()

    click.echo("Starting discovery process...")
