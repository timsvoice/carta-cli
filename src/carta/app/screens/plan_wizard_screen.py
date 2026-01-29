"""Plan wizard screen for implementation Q&A flow."""

from pathlib import Path
from typing import cast

from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, LoadingIndicator
from textual.containers import ScrollableContainer
from textual.worker import Worker, WorkerState

from carta.utils.agent import Agent
from carta.app.screens.mixins import AgentScreenMixin
from carta.app.widgets.prompt_input import PromptInput
from carta.app.widgets.agent_output import AgentOutput
from carta.app.widgets.question_selector import QuestionSelector
from carta.app.messages import PromptSubmitted, QuestionAnswered
from carta.app.types import PlanWizardResult

_prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "plan"


class PlanWizardScreen(Screen[PlanWizardResult], AgentScreenMixin):
    """Screen for plan Q&A flow to gather implementation context.

    First runs the gather agent to generate questions based on discovery,
    then guides user through Q&A.
    Dismisses with PlanWizardResult containing answers on completion.
    """

    DEFAULT_CSS = """
    PlanWizardScreen {
        layout: vertical;
    }

    PlanWizardScreen #question-area {
        height: 1fr;
        padding: 1;
    }

    PlanWizardScreen #loading {
        dock: bottom;
        height: 1;
        margin: 0 2;
    }

    PlanWizardScreen #loading.hidden {
        display: none;
    }

    PlanWizardScreen .completion-message {
        text-style: bold;
        color: $success;
        margin: 1;
    }

    PlanWizardScreen .completion-summary {
        margin-left: 2;
    }
    """

    BINDINGS = [
        ("p", "previous", "Previous"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, discovery_content: str) -> None:
        super().__init__()
        self._discovery_content = discovery_content
        self.questions: list[dict] = []
        self.current_idx = 0
        self.answers: dict[int, int] = {}
        self._gathering_complete = False

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield AgentOutput(id="output")
        yield ScrollableContainer(id="question-area")
        yield LoadingIndicator(id="loading", classes="hidden")
        yield PromptInput(label="Analyzing discovery document...", id="prompt-container")
        yield Footer()

    @property
    def prompt(self) -> PromptInput:
        """Get the prompt input widget."""
        return cast(PromptInput, self.query_one("#prompt-container", PromptInput))

    def on_mount(self) -> None:
        """Start the gather agent when screen mounts."""
        self.output.write_status("Analyzing discovery document for planning questions...")
        self.show_loading()
        self._run_gather_agent()

    def on_prompt_submitted(self, event: PromptSubmitted) -> None:
        """Handle prompt submission from PromptInput widget."""
        if not self._gathering_complete:
            return
        self._handle_input(event.value)

    def on_question_answered(self, event: QuestionAnswered) -> None:
        """Handle QuestionAnswered message from QuestionSelector."""
        if self._gathering_complete:
            self._select_option(event.option_idx)

    @work(thread=True)
    def _run_gather_agent(self) -> dict:
        """Run the gather agent to generate planning questions."""

        def on_tool_call(tool_name: str, args: dict, tokens: int) -> None:
            self.app.call_from_thread(self._on_tool_call, tool_name, args, tokens)

        agent = Agent(on_tool_call=on_tool_call, root_path=".cache")
        system_prompt = (_prompts_dir / "gather.md").read_text()

        response = agent.run(
            f"""
            {system_prompt}

            ## Discovery Document
            {self._discovery_content}
            """
        )

        return response

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.state == WorkerState.SUCCESS:
            if event.worker.name == "_run_gather_agent":
                self._on_gather_complete(event.worker.result)

    def _on_tool_call(self, tool_name: str, args: dict, tokens: int) -> None:
        """Display tool call feedback."""
        self.output.write_tool_call(tool_name, args, tokens)

    def _on_gather_complete(self, response: dict) -> None:
        """Handle gather agent completion."""
        self.hide_loading()

        total_tokens = response.get("total_tokens", 0)
        self.output.write_tokens_summary(total_tokens)

        content = response.get("message", {}).get("content", "")

        # Parse questions from JSON response
        import json

        try:
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```"):
                # Remove markdown code fences if present
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])

            self.questions = json.loads(content)
            self._gathering_complete = True

            # Hide output area, show question area
            self.query_one("#output", AgentOutput).display = False
            self._display_current_question()

        except json.JSONDecodeError as e:
            self.output.write_error(f"Failed to parse questions: {e}")
            self.output.write_status("Raw response:")
            self.output.write(content)
            self.prompt.label = "Press Escape to go back"

    def _handle_input(self, value: str) -> None:
        """Handle wizard option selection."""
        # Navigation commands
        if value.lower() in ("p", "prev", "previous") and self.current_idx > 0:
            self.current_idx -= 1
            self._display_current_question()
            return

        if value.lower() in ("q", "quit"):
            self._cancel()
            return

        # Try to parse as option number
        self._try_select_option(value)

    def action_previous(self) -> None:
        """Go to previous question."""
        if self._gathering_complete and self.current_idx > 0:
            self.current_idx -= 1
            self._display_current_question()

    def action_cancel(self) -> None:
        """Cancel the wizard."""
        self._cancel()

    def _try_select_option(self, value: str) -> None:
        """Try to parse input as option selection."""
        if not self.questions:
            return

        question = self.questions[self.current_idx]

        try:
            option_idx = int(value) - 1
            if 0 <= option_idx < len(question["options"]):
                self._select_option(option_idx)
            else:
                self._show_input_error(
                    f"Please enter a number between 1 and {len(question['options'])}"
                )
        except ValueError:
            self._show_input_error(
                "Enter a number to select an option, 'p' for previous, or 'q' to quit"
            )

    def _show_input_error(self, message: str) -> None:
        """Show an error message for invalid input."""
        container = self.query_one("#question-area", ScrollableContainer)
        error_widget = Static(f"[yellow]{message}[/yellow]", classes="input-error")
        for widget in container.query(".input-error"):
            widget.remove()
        container.mount(error_widget)

    def _display_current_question(self) -> None:
        """Display the current question using QuestionSelector widget."""
        container = self.query_one("#question-area", ScrollableContainer)
        container.remove_children()
        container.mount(
            QuestionSelector(
                question=self.questions[self.current_idx],
                question_idx=self.current_idx,
                total_questions=len(self.questions),
                selected_option=self.answers.get(self.current_idx),
            )
        )

        question = self.questions[self.current_idx]
        self.prompt.label = f"Select option (1-{len(question['options'])}), 'p' previous, 'q' quit"
        self.prompt.focus()

    def _select_option(self, option_idx: int) -> None:
        """Record selection and advance to next question."""
        self.answers[self.current_idx] = option_idx

        if self.current_idx < len(self.questions) - 1:
            self.current_idx += 1
            self._display_current_question()
        else:
            self._complete_wizard()

    def _complete_wizard(self) -> None:
        """Complete the wizard and dismiss with results."""
        results = self._build_results()

        container = self.query_one("#question-area", ScrollableContainer)
        container.remove_children()

        container.mount(Static("Planning Context Gathered", classes="completion-message"))
        for q in results:
            container.mount(
                Static(
                    f"[bold]{q['topic']}:[/bold] {q.get('answer', 'No answer')}",
                    classes="completion-summary",
                )
            )

        self.dismiss(PlanWizardResult(status="completed", answers=results))

    def _cancel(self) -> None:
        """Cancel the wizard."""
        self.dismiss(PlanWizardResult(status="cancelled"))

    def _build_results(self) -> list[dict]:
        """Build output with answers included."""
        results = []
        for idx, question in enumerate(self.questions):
            result = question.copy()
            answer_idx = self.answers.get(idx)
            if answer_idx is not None:
                result["answer"] = question["options"][answer_idx]["description"]
            results.append(result)
        return results
