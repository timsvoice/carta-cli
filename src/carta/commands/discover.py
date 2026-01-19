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


@click.command("discover-gather")
@click.argument("user_message", type=str)
def discover_gather(user_message: str):
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
    message = response["message"]["content"]
    # questions = json.loads(message)
    print(message)


@click.command("discover-draft")
def discover_draft():
    """
    Discover and document requirements for a feature.
    """
    # Build cache of stripped Python files for LLM context
    build_cache()

    agent = Agent(root_path=".cache")
    user_message = """
    [
        {
          "topic": "Scope",
          "question": "What should the new command do?",
          "options": [
            {
              "description": "Generate code from a specification",
              "impact": "Requires parsing spec format, generating code, handling multiple files"
            },
            {
              "description": "Validate existing code against a specification",
              "impact": "Requires comparison logic, reporting discrepancies"
            },
            {
              "description": "Both generate and validate",
              "impact": "More complex but provides complete workflow"
            }
          ],
          "answer": "Generate code from a specification"
        },
        {
          "topic": "Input",
          "question": "How should the command receive input?",
          "options": [
            {
              "description": "File path argument pointing to a spec file",
              "impact": "Simple, follows existing CLI patterns"
            },
            {
              "description": "Interactive prompts to gather requirements",
              "impact": "More user-friendly but slower workflow"
            },
            {
              "description": "Stdin for piping from other commands",
              "impact": "Enables shell composition but less discoverable"
            }
          ],
          "answer": "File path argument pointing to a spec file"
        },
        {
          "topic": "Output",
          "question": "Where should generated code be written?",
          "options": [
            {
              "description": "Directly to the project directory",
              "impact": "Convenient but risks overwriting existing files"
            },
            {
              "description": "To a staging directory for review",
              "impact": "Safer but adds extra step to workflow"
            },
            {
              "description": "Preview to stdout, require confirmation to write",
              "impact": "Balances safety and convenience"
            }
          ],
          "answer": "Preview to stdout, require confirmation to write"
        },
        {
          "topic": "Error Handling",
          "question": "How should the command handle malformed specifications?",
          "options": [
            {
              "description": "Fail fast with validation errors",
              "impact": "Clear feedback but requires valid input upfront"
            },
            {
              "description": "Attempt partial generation with warnings",
              "impact": "More flexible but may produce incomplete output"
            }
          ],
          "answer": "Fail fast with validation errors"
        }
      ]
    """
    system_prompt = (_prompts_dir / "draft.md").read_text()

    response = agent.run(
        f"""
        {system_prompt}
        ## Feature Description
        {user_message}
        """
    )

    message = response["message"]["content"]
    print(message)
