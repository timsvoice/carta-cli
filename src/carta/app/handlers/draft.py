"""Draft handler for running draft agent and displaying results."""

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from carta.agent import Agent
from carta.app.handlers.base import BaseHandler
from carta.app.types import DraftResult

if TYPE_CHECKING:
    from carta.app.app import CartaApp

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "discover"


class DraftHandler(BaseHandler):
    """Handler for running draft agent and displaying discovery document."""

    def __init__(
        self,
        app: "CartaApp",
        on_complete: Callable[[DraftResult], None],
        feature_description: str,
        answers: list[dict],
    ):
        super().__init__(app, on_complete)
        self._feature_description = feature_description
        self._answers = answers
        self._draft_complete = False

    def start(self) -> None:
        """Start the draft agent when handler becomes active."""
        self.app.set_placeholder("Type 'new' to start over, or 'quit' to exit")
        self.app.write_output("\n[dim]Drafting discovery document...[/dim]")
        self.app.show_loading()
        self.app.run_agent_task(self._run_draft_agent)

    def handle_input(self, value: str) -> None:
        """Handle input after draft is complete."""
        if not self._draft_complete:
            return

        value = value.lower()

        if value in ("new", "restart", "again"):
            self.on_complete(DraftResult(status="restart"))
        elif value in ("quit", "exit", "q"):
            self.on_complete(DraftResult(status="done"))
        else:
            self.app.write_output("[yellow]Type 'new' to start over, or 'quit' to exit[/yellow]")

    def _run_draft_agent(self) -> None:
        """Run the draft agent (called in background thread)."""

        def on_tool_call(tool_name: str, args: dict, tokens: int) -> None:
            self.app.call_from_thread(self._on_tool_call, tool_name, args, tokens)

        agent = Agent(on_tool_call=on_tool_call, root_path=".cache")
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

        self.app.call_from_thread(self._on_draft_complete, response)

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

    def _on_draft_complete(self, response: dict) -> None:
        """Handle draft agent completion."""
        self.app.hide_loading()
        self._draft_complete = True

        total_tokens = response.get("total_tokens", 0)
        self.app.write_output(f"[dim]Total tokens used: {total_tokens:,}[/dim]")

        content = response.get("message", {}).get("content", "")

        self.app.write_output("\n[bold green]━━━ Discovery Document Draft ━━━[/bold green]\n")
        self.app.write_output(content)
        self.app.write_output(
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
