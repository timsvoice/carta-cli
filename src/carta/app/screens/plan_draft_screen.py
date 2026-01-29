"""Plan draft screen for running plan agent and displaying results."""

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, LoadingIndicator
from textual.worker import Worker, WorkerState

from carta.utils.agent import Agent
from carta.utils.filename import plan_exists
from carta.app.screens.mixins import AgentScreenMixin
from carta.app.widgets.agent_output import AgentOutput
from carta.app.widgets.prompt_input import PromptInput
from carta.app.messages import PromptSubmitted
from carta.app.types import PlanDraftResult

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "plan"


class PlanDraftScreen(Screen[PlanDraftResult], AgentScreenMixin):
    """Screen for running plan agent and displaying implementation plan.

    Dismisses with PlanDraftResult on user action (approve, restart, quit).
    """

    DEFAULT_CSS = """
    PlanDraftScreen {
        layout: vertical;
    }

    PlanDraftScreen #loading {
        dock: bottom;
        height: 1;
        margin: 0 2;
    }

    PlanDraftScreen #loading.hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("a", "approve", "Approve"),
        ("r", "restart", "Restart"),
    ]

    def __init__(
        self,
        discovery_content: str,
        answers: list[dict],
        feature_path: str,
    ) -> None:
        super().__init__()
        self._discovery_content = discovery_content
        self._answers = answers
        self._feature_path = Path(feature_path)
        self._draft_complete = False
        self._draft_saved = False
        self._current_draft: str = ""
        self._awaiting_overwrite_confirm = False

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield AgentOutput(id="output")
        yield LoadingIndicator(id="loading", classes="hidden")
        yield PromptInput(label="Enter command...", id="prompt-container")
        yield Footer()

    def on_mount(self) -> None:
        """Start the draft agent when screen mounts."""
        self.prompt.label = "Generating implementation plan..."
        self.output.write_status("\nDrafting implementation plan...")
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

        # Handle overwrite confirmation
        if self._awaiting_overwrite_confirm:
            if value_lower in ("y", "yes"):
                self._do_save()
                self._awaiting_overwrite_confirm = False
            elif value_lower in ("n", "no"):
                self._awaiting_overwrite_confirm = False
                self._show_draft_options()
            else:
                self.output.write_warning("Please enter 'y' to overwrite or 'n' to cancel.")
            return

        # After draft is saved, only allow restart or quit
        if self._draft_saved:
            if value_lower in ("new", "restart", "again"):
                self.dismiss(PlanDraftResult(status="restart"))
            elif value_lower in ("quit", "exit", "q"):
                self.dismiss(PlanDraftResult(status="done"))
            else:
                self.output.write_warning("Type 'new' to start another plan, or 'quit' to exit.")
            return

        # Approve and save the draft
        if value_lower in ("approve", "accept", "done", "y", "yes", "a"):
            self._save_draft()
        # Restart the planning flow
        elif value_lower in ("new", "restart", "again"):
            self.dismiss(PlanDraftResult(status="restart"))
        # Exit the application
        elif value_lower in ("quit", "exit", "q"):
            self.dismiss(PlanDraftResult(status="done"))
        # Treat any other input as feedback for refinement
        else:
            self._start_refinement(value)

    def action_approve(self) -> None:
        """Approve and save the draft."""
        if self._draft_complete and not self._draft_saved:
            self._save_draft()

    def action_restart(self) -> None:
        """Restart the planning flow."""
        self.dismiss(PlanDraftResult(status="restart"))

    @work(thread=True)
    def _run_draft_agent(self) -> dict:
        """Run the draft agent in a background thread."""

        def on_tool_call(tool_name: str, args: dict, tokens: int) -> None:
            self.app.call_from_thread(self._on_tool_call, tool_name, args, tokens)

        agent = Agent(on_tool_call=on_tool_call, root_path=".cache")
        system_prompt = (_prompts_dir / "draft.md").read_text()

        qa_text = self._format_qa_for_prompt()

        response = agent.run(
            f"""
            {system_prompt}

            ## Discovery Document
            {self._discovery_content}

            ## Planning Questions and Answers
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

            ## Current Plan
            {self._current_draft}

            ## User Feedback
            {feedback}
            """
        )

        return response

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.state == WorkerState.SUCCESS:
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
        self._current_draft = content.strip()

        self.output.write_header("Implementation Plan Draft")
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
        self.output.write_status("\nType 'new' to create another plan, or 'quit' to exit.")
        self.prompt.label = "new / quit"

    def _save_draft(self) -> None:
        """Save the current draft, with overwrite confirmation if needed."""
        if plan_exists(self._feature_path):
            self._awaiting_overwrite_confirm = True
            self.output.write_warning(f"\nA plan.md already exists in {self._feature_path.name}.")
            self.prompt.label = "Overwrite existing plan? (y/n)"
        else:
            self._do_save()

    def _do_save(self) -> None:
        """Actually save the plan to disk."""
        plan_path = self._feature_path / "plan.md"
        plan_path.write_text(self._current_draft)

        self._draft_saved = True
        self.output.write_success(f"\nPlan saved to {plan_path}")
        self._show_post_save_options()

    def _start_refinement(self, feedback: str) -> None:
        """Start refinement cycle with user feedback."""
        self._draft_complete = False
        self.output.write_status(f"\nRefining plan with feedback: {feedback}")
        self.show_loading()
        self._run_refine_agent(feedback)

    def _on_refine_complete(self, response: dict) -> None:
        """Handle refine agent completion."""
        self.hide_loading()
        self._draft_complete = True

        total_tokens = response.get("total_tokens", 0)
        self.output.write_tokens_summary(total_tokens)

        content = response.get("message", {}).get("content", "")
        self._current_draft = content.strip()

        self.output.write_header("Refined Implementation Plan")
        self.write_output(self._current_draft)
        self._show_draft_options()

    def _format_qa_for_prompt(self) -> str:
        """Format questions and answers for the draft prompt."""
        lines = []
        for q in self._answers:
            lines.append(f"### {q['topic']}")
            lines.append(f"**Question:** {q['question']}")
            answer = q.get("answer", "No answer provided")
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
