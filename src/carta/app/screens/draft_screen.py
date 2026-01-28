"""Draft screen for running draft agent and displaying results."""

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, LoadingIndicator
from textual.worker import Worker, WorkerState

from carta.utils.agent import Agent
from carta.utils.filename import (
    validate_draft_filename,
    get_next_sequence_number,
    format_feature_dirname,
)
from carta.app.screens.mixins import AgentScreenMixin
from carta.app.widgets.agent_output import AgentOutput
from carta.app.widgets.prompt_input import PromptInput
from carta.app.messages import PromptSubmitted
from carta.app.types import DraftResult

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "discover"


class DraftScreen(Screen[DraftResult], AgentScreenMixin):
    """Screen for running draft agent and displaying discovery document.

    Dismisses with DraftResult on user action (approve, restart, quit).
    """

    DEFAULT_CSS = """
    DraftScreen {
        layout: vertical;
    }

    DraftScreen #loading {
        dock: bottom;
        height: 1;
        margin: 0 2;
    }

    DraftScreen #loading.hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("a", "approve", "Approve"),
        ("r", "restart", "Restart"),
    ]

    def __init__(self, feature_description: str, answers: list[dict]) -> None:
        super().__init__()
        self._feature_description = feature_description
        self._answers = answers
        self._draft_complete = False
        self._draft_saved = False
        self._current_draft: str = ""
        self._draft_name: str = ""

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield AgentOutput(id="output")
        yield LoadingIndicator(id="loading", classes="hidden")
        yield PromptInput(label="Enter command...", id="prompt-container")
        yield Footer()

    def on_mount(self) -> None:
        """Start the draft agent when screen mounts."""
        self.prompt.label = "Generating draft..."
        self.output.write_status("\nDrafting discovery document...")
        self.show_loading()
        self._run_draft_agent()

    def on_prompt_submitted(self, event: PromptSubmitted) -> None:
        """Handle prompt submission from PromptInput widget."""
        self.handle_input(event.value)

    def handle_input(self, value: str) -> None:
        """Handle input after draft is complete."""
        if not self._draft_complete:
            return

        value_lower = value.lower().strip()

        # After draft is saved, only allow new or quit
        if self._draft_saved:
            if value_lower in ("new", "restart", "again"):
                self.dismiss(DraftResult(status="restart"))
            elif value_lower in ("quit", "exit", "q"):
                self.dismiss(DraftResult(status="done"))
            else:
                self.output.write_warning(
                    "Type 'new' to start another discovery, or 'quit' to exit."
                )
            return

        # Approve and save the draft
        if value_lower in ("approve", "accept", "done", "y", "yes", "a"):
            self._save_draft()
            self._draft_saved = True
            self._show_post_save_options()
        # Restart the discovery flow
        elif value_lower in ("new", "restart", "again"):
            self.dismiss(DraftResult(status="restart"))
        # Exit the application
        elif value_lower in ("quit", "exit", "q"):
            self.dismiss(DraftResult(status="done"))
        # Treat any other input as feedback for refinement
        else:
            self._start_refinement(value)

    def action_approve(self) -> None:
        """Approve and save the draft."""
        if self._draft_complete and not self._draft_saved:
            self._save_draft()
            self._draft_saved = True
            self._show_post_save_options()

    def action_restart(self) -> None:
        """Restart the discovery flow."""
        self.dismiss(DraftResult(status="restart"))

    @work(thread=True)
    def _run_draft_agent(self) -> dict:
        """Run the draft agent in a background thread."""

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

        return response

    @work(thread=True)
    def _run_refine_agent(self, feedback: str) -> dict:
        """Run the refine agent with user feedback in a background thread."""

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

        return response

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.state == WorkerState.SUCCESS:
            # Check which worker completed based on the function name
            if event.worker.name == "_run_draft_agent":
                self._on_draft_complete(event.worker.result)
            elif event.worker.name == "_run_refine_agent":
                self._on_refine_complete(event.worker.result)

    def _on_tool_call(self, tool_name: str, args: dict, tokens: int) -> None:
        """Display tool call feedback using AgentOutput widget."""
        self.output.write_tool_call(tool_name, args, tokens)

    def _on_draft_complete(self, response: dict) -> None:
        """Handle draft agent completion."""
        self.hide_loading()
        self._draft_complete = True

        total_tokens = response.get("total_tokens", 0)
        self.output.write_tokens_summary(total_tokens)

        content = response.get("message", {}).get("content", "")

        # Parse filename and draft content from response
        self._draft_name, self._current_draft = self._parse_draft_response(content)

        self.output.write_header("Discovery Document Draft")
        self.write_output(self._current_draft)
        self._show_draft_options()

    def _show_draft_options(self) -> None:
        """Display options after draft is shown."""
        self.output.write_status(
            "\nType 'approve' to accept and save, 'new' to start over, "
            "'quit' to exit, or provide feedback to refine."
        )
        self.prompt.label = "approve / new / quit / or type feedback to refine"

    def _show_post_save_options(self) -> None:
        """Display options after draft has been saved."""
        self.output.write_status("\nType 'new' to start another discovery, or 'quit' to exit.")
        self.prompt.label = "new / quit"

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
                self.output.write_warning(
                    f"Note: Filename '{raw_filename}' normalized to '{filename}'"
                )

            # Skip the filename line and any blank lines after it
            draft_start = 1
            while draft_start < len(lines) and not lines[draft_start].strip():
                draft_start += 1

        # Fallback if no filename found
        if not filename:
            filename = "untitled-feature"
            self.output.write_warning(
                "Note: No FILENAME found in response, using 'untitled-feature'"
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

        self.output.write_success(f"\nDraft saved to {discovery_path}")
        self.output.write_status(f"Feature directory: {feature_dir}")

    def _start_refinement(self, feedback: str) -> None:
        """Start refinement cycle with user feedback."""
        self._draft_complete = False
        self.output.write_status(f"\nRefining draft with feedback: {feedback}")
        self.show_loading()
        self._run_refine_agent(feedback)

    def _on_refine_complete(self, response: dict) -> None:
        """Handle refine agent completion."""
        self.hide_loading()
        self._draft_complete = True

        total_tokens = response.get("total_tokens", 0)
        self.output.write_tokens_summary(total_tokens)

        content = response.get("message", {}).get("content", "")

        # Update current draft (filename stays the same)
        self._current_draft = content.strip()

        self.output.write_header("Refined Discovery Document")
        self.write_output(self._current_draft)
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
