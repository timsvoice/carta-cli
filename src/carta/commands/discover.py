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

    # TODO: First gather requirements from the user in text input form
    # TODO: Pass the requirements to the agent to generate disambiguation questions
    # TODO: Gather user responses to the disambiguation questions
    # TODO: Use answers to generate the first draft of the discovery document
    # TODO: Request user approval for the draft
    # TODO: Iterate
    # TODO: Save the final discovery document to the .carta directory
