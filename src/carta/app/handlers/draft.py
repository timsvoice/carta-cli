"""Draft handler for running draft agent and displaying results."""

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from carta.utils.agent import Agent
from carta.utils.filename import (
    validate_draft_filename,
    get_next_sequence_number,
    format_feature_dirname,
)
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
        self._draft_saved = False
        self._current_draft: str = ""
        self._draft_name: str = ""

    def start(self) -> None:
        """Start the draft agent when handler becomes active."""
        self.app.set_placeholder("Generating draft...")
        self.app.write_output("\n[dim]Drafting discovery document...[/dim]")
        self.app.show_loading()
        self.app.run_agent_task(self._run_draft_agent)

    def handle_input(self, value: str) -> None:
        """Handle input after draft is complete."""
        if not self._draft_complete:
            return

        value_lower = value.lower().strip()

        # After draft is saved, only allow new or quit
        if self._draft_saved:
            if value_lower in ("new", "restart", "again"):
                self.on_complete(DraftResult(status="restart"))
            elif value_lower in ("quit", "exit", "q"):
                self.on_complete(DraftResult(status="done"))
            else:
                self.app.write_output(
                    "[yellow]Type 'new' to start another discovery, or 'quit' to exit.[/yellow]"
                )
            return

        # Approve and save the draft
        if value_lower in ("approve", "accept", "done", "y", "yes"):
            self._save_draft()
            self._draft_saved = True
            self._show_post_save_options()
        # Restart the discovery flow
        elif value_lower in ("new", "restart", "again"):
            self.on_complete(DraftResult(status="restart"))
        # Exit the application
        elif value_lower in ("quit", "exit", "q"):
            self.on_complete(DraftResult(status="done"))
        # Treat any other input as feedback for refinement
        else:
            self._start_refinement(value)

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

        # Parse filename and draft content from response
        self._draft_name, self._current_draft = self._parse_draft_response(content)

        self.app.write_output("\n[bold green]━━━ Discovery Document Draft ━━━[/bold green]\n")
        self.app.write_output(self._current_draft)
        self._show_draft_options()

    def _show_draft_options(self) -> None:
        """Display options after draft is shown."""
        self.app.write_output(
            "\n[dim]Type 'approve' to accept and save, 'new' to start over, "
            "'quit' to exit, or provide feedback to refine.[/dim]"
        )
        self.app.set_placeholder("approve / new / quit / or type feedback to refine")

    def _show_post_save_options(self) -> None:
        """Display options after draft has been saved."""
        self.app.write_output(
            "\n[dim]Type 'new' to start another discovery, or 'quit' to exit.[/dim]"
        )
        self.app.set_placeholder("new / quit")

    def _parse_draft_response(self, content: str) -> tuple[str, str]:
        """Parse filename and draft content from agent response.

        Expected format:
            FILENAME: some-name-here

            **Objective**
            ...

        Returns:
            A tuple of (validated_filename, draft_content).
        """
        lines = content.strip().split("\n")
        filename = None
        draft_start = 0

        # Look for FILENAME: line at the start
        if lines and lines[0].upper().startswith("FILENAME:"):
            raw_filename = lines[0].split(":", 1)[1].strip()
            filename, is_valid = validate_draft_filename(raw_filename)

            if not is_valid:
                self.app.write_output(
                    f"[yellow]Note: Filename '{raw_filename}' normalized to '{filename}'[/yellow]"
                )

            # Skip the filename line and any blank lines after it
            draft_start = 1
            while draft_start < len(lines) and not lines[draft_start].strip():
                draft_start += 1

        # Fallback if no filename found
        if not filename:
            filename = "untitled-feature"
            self.app.write_output(
                "[yellow]Note: No FILENAME found in response, using 'untitled-feature'[/yellow]"
            )

        draft_content = "\n".join(lines[draft_start:])
        return filename, draft_content

    def _get_next_feature_dir(self) -> Path:
        """Get the next feature directory path with sequence prefix.

        Returns:
            Path to the new feature directory (e.g., .carta/001-user-auth/).
        """
        carta_dir = Path(".carta")
        carta_dir.mkdir(exist_ok=True)

        sequence = get_next_sequence_number(carta_dir)
        dirname = format_feature_dirname(sequence, self._draft_name)

        return carta_dir / dirname

    def _save_draft(self) -> None:
        """Save the current draft to the feature directory structure.

        Creates:
            .carta/{NNN}-{name}/
            ├── discovery.md  (the draft content)
            ├── plan.md       (empty placeholder)
            └── implementation.md (empty placeholder)
        """
        feature_dir = self._get_next_feature_dir()
        feature_dir.mkdir(exist_ok=True)

        # Save the discovery document
        discovery_path = feature_dir / "discovery.md"
        discovery_path.write_text(self._current_draft)

        # Create placeholder files for plan and implementation
        (feature_dir / "plan.md").touch()
        (feature_dir / "implementation.md").touch()

        self.app.write_output(f"\n[bold green]Draft saved to {discovery_path}[/bold green]")
        self.app.write_output(f"[dim]Feature directory: {feature_dir}[/dim]")

    def _start_refinement(self, feedback: str) -> None:
        """Start refinement cycle with user feedback."""
        self._draft_complete = False
        self.app.write_output(f"\n[dim]Refining draft with feedback: {feedback}[/dim]")
        self.app.show_loading()
        self.app.run_agent_task(lambda: self._run_refine_agent(feedback))

    def _run_refine_agent(self, feedback: str) -> None:
        """Run the refine agent with user feedback (called in background thread)."""

        def on_tool_call(tool_name: str, args: dict, tokens: int) -> None:
            self.app.call_from_thread(self._on_tool_call, tool_name, args, tokens)

        agent = Agent(on_tool_call=on_tool_call, root_path=".cache")
        refine_prompt = (_prompts_dir / "refine.md").read_text()

        response = agent.run(
            f"""
            {refine_prompt}

            ## Current Draft
            {self._current_draft}

            ## User Feedback
            {feedback}
            """
        )

        self.app.call_from_thread(self._on_refine_complete, response)

    def _on_refine_complete(self, response: dict) -> None:
        """Handle refine agent completion."""
        self.app.hide_loading()
        self._draft_complete = True

        total_tokens = response.get("total_tokens", 0)
        self.app.write_output(f"[dim]Total tokens used: {total_tokens:,}[/dim]")

        content = response.get("message", {}).get("content", "")

        # Update current draft (filename stays the same)
        self._current_draft = content.strip()

        self.app.write_output("\n[bold green]━━━ Refined Discovery Document ━━━[/bold green]\n")
        self.app.write_output(self._current_draft)
        self._show_draft_options()

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
