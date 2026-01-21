"""Draft screen for running draft agent and displaying results."""

from pathlib import Path

from textual.widgets import Input
from textual.worker import get_current_worker
from textual import work

from carta.agent import Agent
from carta.app.screens.base import BaseScreen
from carta.app.types import DraftResult

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "discover"


class DraftScreen(BaseScreen[DraftResult]):
    """Screen for running draft agent and displaying discovery document."""

    def __init__(self, feature_description: str, answers: list[dict]):
        super().__init__(input_placeholder="Type 'new' to start over, or 'quit' to exit")
        self._feature_description = feature_description
        self._answers = answers
        self._draft_complete = False

    def on_mount(self) -> None:
        """Start the draft agent when mounted."""
        self.write_output("\n[dim]Drafting discovery document...[/dim]")
        self.show_loading()
        self._run_draft_agent()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input after draft is complete."""
        if not self._draft_complete:
            return

        value = event.value.strip().lower()
        if not value:
            return

        self.query_one("#user-input", Input).value = ""

        if value in ("new", "restart", "again"):
            self.dismiss(DraftResult(status="restart"))
        elif value in ("quit", "exit", "q"):
            self.dismiss(DraftResult(status="done"))
        else:
            self.write_output("[yellow]Type 'new' to start over, or 'quit' to exit[/yellow]")

    @work(thread=True)
    def _run_draft_agent(self) -> None:
        """Run the draft agent in a background thread."""
        worker = get_current_worker()

        def on_tool_call(tool_name: str, args: dict) -> None:
            if worker.is_cancelled:
                return
            self.app.call_from_thread(self._on_tool_call, tool_name, args)

        agent = Agent(on_tool_call=on_tool_call)
        system_prompt = (_prompts_dir / "draft.md").read_text()

        # Format Q&A for the prompt
        qa_text = self._format_qa_for_prompt()

        response = agent.run(
            f"""
            {system_prompt}

            ## Feature Description
            {self._feature_description}

            ## Questions and Answers
            {qa_text}
            """
        )

        if not worker.is_cancelled:
            self.app.call_from_thread(self._on_draft_complete, response)

    def _on_tool_call(self, tool_name: str, args: dict) -> None:
        """Display tool call feedback in the UI."""
        if tool_name == "file_read":
            path = args.get("path", "unknown")
            self.write_output(f"  [dim]> Reading {path}[/dim]")
        elif tool_name == "list_files":
            path = args.get("path", ".")
            self.write_output(f"  [dim]> Listing {path}[/dim]")

    def _on_draft_complete(self, response: dict) -> None:
        """Handle draft agent completion."""
        self.hide_loading()
        self._draft_complete = True

        content = response.get("message", {}).get("content", "")

        self.write_output("\n[bold green]━━━ Discovery Document Draft ━━━[/bold green]\n")
        self.write_output(content)
        self.write_output(
            "\n[dim]Draft complete. Type 'new' to start over, or 'quit' to exit.[/dim]"
        )

    def _format_qa_for_prompt(self) -> str:
        """Format questions and answers for the draft prompt."""
        lines = []
        for q in self._answers:
            lines.append(f"### {q['topic']}")
            lines.append(f"**Question:** {q['question']}")
            answer = q.get("answer", "No answer provided")
            # Find the impact for the selected answer
            impact = ""
            for opt in q["options"]:
                if opt["description"] == answer:
                    impact = opt["impact"]
                    break
            lines.append(f"**Answer:** {answer}")
            if impact:
                lines.append(f"**Impact:** {impact}")
            lines.append("")
        return "\n".join(lines)
