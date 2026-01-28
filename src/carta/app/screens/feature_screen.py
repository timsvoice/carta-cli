"""Feature input screen with gather agent."""

import json
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, LoadingIndicator
from textual.worker import Worker, WorkerState

from carta.utils.agent import Agent
from carta.app.screens.mixins import AgentScreenMixin
from carta.app.widgets.agent_output import AgentOutput
from carta.app.widgets.prompt_input import PromptInput
from carta.app.messages import PromptSubmitted
from carta.app.types import FeatureResult

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "discover"


class FeatureScreen(Screen[FeatureResult], AgentScreenMixin):
    """Screen for entering feature description and running gather agent.

    Dismisses with FeatureResult containing questions on success.
    """

    DEFAULT_CSS = """
    FeatureScreen {
        layout: vertical;
    }

    FeatureScreen #loading {
        dock: bottom;
        height: 1;
        margin: 0 2;
    }

    FeatureScreen #loading.hidden {
        display: none;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._feature_description: str = ""

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield AgentOutput(id="output")
        yield LoadingIndicator(id="loading", classes="hidden")
        yield PromptInput(label="Describe your feature", id="prompt-container")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen when it mounts."""
        self.prompt.focus()

    def on_prompt_submitted(self, event: PromptSubmitted) -> None:
        """Handle prompt submission from PromptInput widget."""
        self.handle_input(event.value)

    def handle_input(self, value: str) -> None:
        """Handle feature description submission."""
        self._feature_description = value

        self.write_output(f"\n[bold]Feature:[/bold] {value}")
        self.output.write_status("Gathering requirements from codebase...")

        self.show_loading()
        self._run_gather_agent()

    @work(thread=True)
    def _run_gather_agent(self) -> dict:
        """Run the gather agent in a background thread."""

        def on_tool_call(tool_name: str, args: dict, tokens: int) -> None:
            self.app.call_from_thread(self._on_tool_call, tool_name, args, tokens)

        agent = Agent(on_tool_call=on_tool_call, root_path=".cache")
        system_prompt = (_prompts_dir / "gather.md").read_text()

        response = agent.run(
            f"""
            {system_prompt}
            ## Feature Description
            {self._feature_description}
            """
        )

        return response

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.state == WorkerState.SUCCESS:
            self._on_gather_complete(event.worker.result)

    def _on_tool_call(self, tool_name: str, args: dict, tokens: int) -> None:
        """Display tool call feedback using AgentOutput widget."""
        self.output.write_tool_call(tool_name, args, tokens)

    def _on_gather_complete(self, response: dict) -> None:
        """Handle gather agent completion."""
        self.hide_loading()

        total_tokens = response.get("total_tokens", 0)
        self.output.write_tokens_summary(total_tokens)

        content = response.get("message", {}).get("content", "")
        questions = self._parse_questions(content)

        if questions:
            self.output.write_success(f"\nFound {len(questions)} questions to clarify.\n")
            self.dismiss(
                FeatureResult(
                    status="success",
                    feature_description=self._feature_description,
                    questions=questions,
                )
            )
        else:
            self.output.write_error("Failed to parse questions from response.")
            self.output.write_status(f"Raw response: {content}")
            self.dismiss(
                FeatureResult(
                    status="error",
                    feature_description=self._feature_description,
                    error="Failed to parse questions from response",
                )
            )

    def _parse_questions(self, response: str) -> list[dict] | None:
        """Parse questions JSON from agent response."""
        try:
            result: list[dict] = json.loads(response.strip())
            return result
        except json.JSONDecodeError:
            try:
                start = response.find("[")
                end = response.rfind("]") + 1
                if start != -1 and end > start:
                    result = json.loads(response[start:end])
                    return result
            except json.JSONDecodeError:
                pass
        return None
