"""Wizard screen for Q&A flow."""

from textual.widgets import Input

from carta.app.screens.base import BaseScreen
from carta.app.types import WizardResult


class WizardScreen(BaseScreen[WizardResult]):
    """Screen for wizard Q&A flow to gather requirements."""

    BINDINGS = [
        ("escape", "cancel", "Cancel wizard"),
    ]

    def __init__(self, questions: list[dict]):
        super().__init__(input_placeholder="")
        self.questions = questions
        self.current_idx = 0
        self.answers: dict[int, int] = {}

    def on_mount(self) -> None:
        """Display the first question when mounted."""
        self._display_current_question()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle wizard option selection."""
        value = event.value.strip()
        if not value:
            return

        self.query_one("#user-input", Input).value = ""

        # Navigation commands
        if value.lower() in ("p", "prev", "previous") and self.current_idx > 0:
            self.current_idx -= 1
            self._display_current_question()
            return

        if value.lower() in ("q", "quit"):
            self.action_cancel()
            return

        # Try to parse as option number
        self._try_select_option(value)

    def _try_select_option(self, value: str) -> None:
        """Try to parse input as option selection."""
        question = self.questions[self.current_idx]

        try:
            option_idx = int(value) - 1  # Convert 1-based to 0-based
            if 0 <= option_idx < len(question["options"]):
                self._select_option(option_idx)
            else:
                self.write_output(
                    f"[yellow]Please enter a number between 1 and {len(question['options'])}[/yellow]"
                )
        except ValueError:
            self.write_output(
                "[yellow]Enter a number to select an option, 'p' for previous, or 'q' to quit[/yellow]"
            )

    def _display_current_question(self) -> None:
        """Display the current question with options."""
        question = self.questions[self.current_idx]
        total = len(self.questions)
        idx = self.current_idx

        # Progress indicator
        progress = "█" * (idx + 1) + "░" * (total - idx - 1)
        percent = int(((idx + 1) / total) * 100)

        self.write_output(
            f"[bold cyan]Question {idx + 1} of {total}: {question['topic']}[/bold cyan]"
        )
        self.write_output(f"[dim]{progress} {percent}%[/dim]\n")
        self.write_output(f"[italic]{question['question']}[/italic]\n")

        # Display options
        for i, opt in enumerate(question["options"]):
            prefix = "  "
            # Show checkmark if previously answered
            if self.answers.get(idx) == i:
                prefix = "[green]✓ [/green]"
            self.write_output(f"{prefix}[bold]{i + 1}.[/bold] {opt['description']}")
            self.write_output(f"      [dim]Impact: {opt['impact']}[/dim]")

        self.write_output("")

        # Update input placeholder
        self.set_placeholder(
            f"Select option (1-{len(question['options'])}), 'p' previous, 'q' quit"
        )

    def _select_option(self, option_idx: int) -> None:
        """Record selection and advance to next question."""
        question = self.questions[self.current_idx]
        selected = question["options"][option_idx]

        self.answers[self.current_idx] = option_idx
        self.write_output(f"[green]→ Selected: {selected['description']}[/green]\n")

        # Advance to next question or complete
        if self.current_idx < len(self.questions) - 1:
            self.current_idx += 1
            self._display_current_question()
        else:
            self._complete_wizard()

    def _complete_wizard(self) -> None:
        """Complete the wizard and dismiss with results."""
        results = self._build_results()

        self.write_output("[bold green]━━━ Requirements Gathered ━━━[/bold green]\n")

        for q in results:
            self.write_output(f"[bold]{q['topic']}:[/bold] {q.get('answer', 'No answer')}")

        self.dismiss(WizardResult(status="completed", answers=results))

    def action_cancel(self) -> None:
        """Cancel the wizard."""
        self.write_output("[yellow]Wizard cancelled.[/yellow]\n")
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
