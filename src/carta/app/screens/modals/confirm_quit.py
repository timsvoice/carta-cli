"""Confirm quit modal screen."""

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal


class ConfirmQuitScreen(ModalScreen[bool]):
    """Modal screen for confirming application quit.

    Dismisses with True to quit, False to cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold yellow]Quit Carta?[/bold yellow]", classes="confirm-title")
            yield Static(
                "Are you sure you want to quit?",
                classes="confirm-message",
            )
            yield Static(
                "[dim]Unsaved changes will be lost.[/dim]",
                classes="confirm-hint",
            )
            with Horizontal():
                yield Button("Yes (y)", variant="warning", id="yes")
                yield Button("No (n)", variant="primary", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm(self) -> None:
        """Confirm quit."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel quit."""
        self.dismiss(False)
