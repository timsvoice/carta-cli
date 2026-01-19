from pathlib import Path

import click

from carta.agent import Agent
from carta.utils.cache import build_cache

_prompts_dir = Path(__file__).parent.parent / "prompts" / "discover"

"""
The purpose of the Discover module is to gather context from the codebase and develop a high-level design document.

@TODO: Add discover prompt (old spec prompt)
@TODO: Add a module for interacting with the LLM
@TODO: Add a function for performing an agentic tool loop for context gathering
"""


@click.command()
@click.argument("user_message", type=str)
def discover(user_message: str):
    """
    Discover and document requirements for a feature.
    """
    # Build cache of stripped Python files for LLM context
    build_cache()

    agent = Agent(root_path=".cache")

    system_prompt = (_prompts_dir / "gather.md").read_text()

    response = agent.run(
        f"""
        {system_prompt}
        ## Feature Description
        {user_message}
        """
    )
    print(response)
