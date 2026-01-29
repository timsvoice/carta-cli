"""Confirm overwrite modal screen."""

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal


class ConfirmOverwriteScreen(ModalScreen[bool]):
    """Modal screen for confirming file overwrite.

    Dismisses with True to overwrite, False to cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    def __init__(self, filename: str = "plan.md") -> None:
        super().__init__()
        self._filename = filename

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                "[bold yellow]Overwrite existing file?[/bold yellow]", classes="confirm-title"
            )
            yield Static(
                f"A {self._filename} already exists in this feature directory.",
                classes="confirm-message",
            )
            yield Static(
                "[dim]The existing file will be replaced.[/dim]",
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
        """Confirm overwrite."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel overwrite."""
        self.dismiss(False)
