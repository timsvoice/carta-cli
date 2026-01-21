"""Feature input screen with gather agent."""

import json
from pathlib import Path

from textual.widgets import Input
from textual.worker import get_current_worker
from textual import work

from carta.agent import Agent
from carta.app.screens.base import BaseScreen
from carta.app.types import FeatureResult

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "discover"


class FeatureScreen(BaseScreen[FeatureResult]):
    """Screen for entering feature description and running gather agent."""

    def __init__(self):
        super().__init__(input_placeholder="Describe your feature...")
        self._feature_description: str = ""

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle feature description submission."""
        value = event.value.strip()
        if not value:
            return

        self.query_one("#user-input", Input).value = ""
        self._feature_description = value

        self.write_output(f"\n[bold]Feature:[/bold] {value}")
        self.write_output("[dim]Gathering requirements from codebase...[/dim]")

        self.show_loading()
        self._run_gather_agent(value)

    @work(thread=True)
    def _run_gather_agent(self, user_message: str) -> None:
        """Run the gather agent in a background thread."""
        worker = get_current_worker()

        def on_tool_call(tool_name: str, args: dict) -> None:
            if worker.is_cancelled:
                return
            self.app.call_from_thread(self._on_tool_call, tool_name, args)

        agent = Agent(on_tool_call=on_tool_call)
        system_prompt = (_prompts_dir / "gather.md").read_text()

        response = agent.run(
            f"""
            {system_prompt}
            ## Feature Description
            {user_message}
            """
        )

        if not worker.is_cancelled:
            self.app.call_from_thread(self._on_gather_complete, response)

    def _on_tool_call(self, tool_name: str, args: dict) -> None:
        """Display tool call feedback in the UI."""
        if tool_name == "file_read":
            path = args.get("path", "unknown")
            self.write_output(f"  [dim]> Reading {path}[/dim]")
        elif tool_name == "list_files":
            path = args.get("path", ".")
            self.write_output(f"  [dim]> Listing {path}[/dim]")

    def _on_gather_complete(self, response: dict) -> None:
        """Handle gather agent completion - dismiss with result."""
        self.hide_loading()

        content = response.get("message", {}).get("content", "")
        questions = self._parse_questions(content)

        if questions:
            self.write_output(f"[green]Found {len(questions)} questions to clarify.[/green]\n")
            self.dismiss(
                FeatureResult(
                    status="success",
                    feature_description=self._feature_description,
                    questions=questions,
                )
            )
        else:
            self.write_output("[red]Failed to parse questions from response.[/red]")
            self.write_output(f"[dim]Raw response: {content}[/dim]")
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
