import click

from carta.utils.cache import build_cache

"""
The purpose of the Research module is to gather context from the codebase and develop a high-level design document.

@TODO: Add research prompt (old spec prompt)
@TODO: Add a module for interacting with the LLM
@TODO: Add a function for performing an agentic tool loop for context gathering
"""


@click.command()
def research():
    """
    Research the given topic and return the results.
    """
    # Build cache of stripped Python files for LLM context
    build_cache()

    click.echo("Researching the given topic...")
