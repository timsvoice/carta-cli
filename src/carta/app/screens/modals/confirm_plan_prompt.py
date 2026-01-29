"""Confirm plan prompt modal screen."""

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal


class ConfirmPlanPromptScreen(ModalScreen[bool]):
    """Modal screen for prompting user to create an implementation plan.

    Shown after completing a discovery document.
    Dismisses with True to continue to planning, False to skip.
    """

    BINDINGS = [
        ("escape", "cancel", "Skip"),
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                "[bold green]Discovery Complete![/bold green]",
                classes="confirm-title",
            )
            yield Static(
                "Would you like to create an implementation plan for this feature?",
                classes="confirm-message",
            )
            yield Static(
                "[dim]You can also create plans later from the main menu.[/dim]",
                classes="confirm-hint",
            )
            with Horizontal():
                yield Button("Yes (y)", variant="success", id="yes")
                yield Button("Skip (n)", variant="default", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm(self) -> None:
        """Continue to planning."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Skip planning."""
        self.dismiss(False)
