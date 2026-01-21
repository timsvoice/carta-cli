"""Feature input handler with gather agent."""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from carta.agent import Agent
from carta.app.handlers.base import BaseHandler
from carta.app.types import FeatureResult

if TYPE_CHECKING:
    from carta.app.app import CartaApp

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "discover"


class FeatureHandler(BaseHandler):
    """Handler for entering feature description and running gather agent."""

    def __init__(self, app: "CartaApp", on_complete: Callable[[FeatureResult], None]):
        super().__init__(app, on_complete)
        self._feature_description: str = ""

    def start(self) -> None:
        """Set up the handler when it becomes active."""
        self.app.set_placeholder("Describe your feature...")

    def handle_input(self, value: str) -> None:
        """Handle feature description submission."""
        self._feature_description = value

        self.app.write_output(f"\n[bold]Feature:[/bold] {value}")
        self.app.write_output("[dim]Gathering requirements from codebase...[/dim]")

        self.app.show_loading()
        self.app.run_agent_task(self._run_gather_agent)

    def _run_gather_agent(self) -> None:
        """Run the gather agent (called in background thread)."""

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

        self.app.call_from_thread(self._on_gather_complete, response)

    def _on_tool_call(self, tool_name: str, args: dict, tokens: int) -> None:
        """Display tool call feedback in the UI."""
        token_str = f"({tokens:,} tokens)"
        result = args.get("_result", "")
        # Truncate result for display
        result_preview = result[:200] + "..." if len(result) > 200 else result
        result_lines = len(result.split("\n"))
        result_chars = len(result)

        if tool_name == "file_read":
            path = args.get("path", "unknown")
            self.app.write_output(f"  [dim]> Reading {path} {token_str}[/dim]")
            self.app.write_output(
                f"    [dim]Result: {result_chars} chars, {result_lines} lines[/dim]"
            )
        elif tool_name == "list_files":
            path = args.get("path", ".")
            self.app.write_output(f"  [dim]> Listing {path} {token_str}[/dim]")
            self.app.write_output(f"    [dim]Result: {result_preview}[/dim]")

    def _on_gather_complete(self, response: dict) -> None:
        """Handle gather agent completion."""
        self.app.hide_loading()

        total_tokens = response.get("total_tokens", 0)
        self.app.write_output(f"[dim]Total tokens used: {total_tokens:,}[/dim]\n")

        content = response.get("message", {}).get("content", "")
        questions = self._parse_questions(content)

        if questions:
            self.app.write_output(f"[green]Found {len(questions)} questions to clarify.[/green]\n")
            self.on_complete(
                FeatureResult(
                    status="success",
                    feature_description=self._feature_description,
                    questions=questions,
                )
            )
        else:
            self.app.write_output("[red]Failed to parse questions from response.[/red]")
            self.app.write_output(f"[dim]Raw response: {content}[/dim]")
            self.on_complete(
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
