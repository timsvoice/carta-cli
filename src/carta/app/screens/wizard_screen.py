"""Wizard screen for Q&A flow."""

from typing import cast

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import ScrollableContainer

from carta.app.widgets.prompt_input import PromptInput
from carta.app.widgets.question_selector import QuestionSelector
from carta.app.messages import PromptSubmitted, QuestionAnswered
from carta.app.types import WizardResult


class WizardScreen(Screen[WizardResult]):
    """Screen for wizard Q&A flow to gather requirements.

    Dismisses with WizardResult containing answers on completion.
    Uses QuestionSelector widget to display questions properly.
    """

    DEFAULT_CSS = """
    WizardScreen {
        layout: vertical;
    }

    WizardScreen #question-area {
        height: 1fr;
        padding: 1;
    }

    WizardScreen .completion-message {
        text-style: bold;
        color: $success;
        margin: 1;
    }

    WizardScreen .completion-summary {
        margin-left: 2;
    }
    """

    BINDINGS = [
        ("p", "previous", "Previous"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, questions: list[dict]) -> None:
        super().__init__()
        self.questions = questions
        self.current_idx = 0
        self.answers: dict[int, int] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield ScrollableContainer(id="question-area")
        yield PromptInput(label="Select an option", id="prompt-container")
        yield Footer()

    @property
    def prompt(self) -> PromptInput:
        """Get the prompt input widget."""
        return cast(PromptInput, self.query_one("#prompt-container", PromptInput))

    def on_mount(self) -> None:
        """Display the first question when screen mounts."""
        self._display_current_question()

    def on_prompt_submitted(self, event: PromptSubmitted) -> None:
        """Handle prompt submission from PromptInput widget."""
        self._handle_input(event.value)

    def on_question_answered(self, event: QuestionAnswered) -> None:
        """Handle QuestionAnswered message from QuestionSelector."""
        self._select_option(event.option_idx)

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
        if self.current_idx > 0:
            self.current_idx -= 1
            self._display_current_question()

    def action_cancel(self) -> None:
        """Cancel the wizard."""
        self._cancel()

    def _try_select_option(self, value: str) -> None:
        """Try to parse input as option selection."""
        question = self.questions[self.current_idx]

        try:
            option_idx = int(value) - 1  # Convert 1-based to 0-based
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
        # Add error message below the question selector
        error_widget = Static(f"[yellow]{message}[/yellow]", classes="input-error")
        # Remove any existing error messages first
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

        # Update input label
        question = self.questions[self.current_idx]
        self.prompt.label = f"Select option (1-{len(question['options'])}), 'p' previous, 'q' quit"
        self.prompt.focus()

    def _select_option(self, option_idx: int) -> None:
        """Record selection and advance to next question."""
        self.answers[self.current_idx] = option_idx

        # Advance to next question or complete
        if self.current_idx < len(self.questions) - 1:
            self.current_idx += 1
            self._display_current_question()
        else:
            self._complete_wizard()

    def _complete_wizard(self) -> None:
        """Complete the wizard and dismiss with results."""
        results = self._build_results()

        # Show completion summary in the question area
        container = self.query_one("#question-area", ScrollableContainer)
        container.remove_children()

        container.mount(Static("Requirements Gathered", classes="completion-message"))
        for q in results:
            container.mount(
                Static(
                    f"[bold]{q['topic']}:[/bold] {q.get('answer', 'No answer')}",
                    classes="completion-summary",
                )
            )

        self.dismiss(WizardResult(status="completed", answers=results))

    def _cancel(self) -> None:
        """Cancel the wizard."""
        self.dismiss(WizardResult(status="cancelled"))

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
