"""Help modal screen."""

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical


class HelpScreen(ModalScreen[None]):
    """Modal screen displaying help information and keybindings.

    Dismisses with None on Escape or Enter.
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("enter", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold cyan]Carta Help[/bold cyan]", classes="help-title")

            yield Static("[bold]Workflow[/bold]", classes="help-section")
            yield Static(
                "1. Describe your feature in natural language",
                classes="help-item",
            )
            yield Static(
                "2. Answer clarifying questions from the wizard",
                classes="help-item",
            )
            yield Static(
                "3. Review and refine the generated discovery document",
                classes="help-item",
            )
            yield Static(
                "4. Approve to save, or provide feedback to refine",
                classes="help-item",
            )

            yield Static("[bold]Global Keybindings[/bold]", classes="help-section")
            yield Static("[cyan]?[/cyan]  Show this help", classes="help-item")
            yield Static("[cyan]q[/cyan]  Quit application", classes="help-item")

            yield Static("[bold]Wizard Screen[/bold]", classes="help-section")
            yield Static("[cyan]1-9[/cyan]  Select option by number", classes="help-item")
            yield Static("[cyan]p[/cyan]  Go to previous question", classes="help-item")
            yield Static("[cyan]Esc[/cyan]  Cancel wizard", classes="help-item")

            yield Static("[bold]Draft Screen[/bold]", classes="help-section")
            yield Static("[cyan]a[/cyan]  Approve and save draft", classes="help-item")
            yield Static("[cyan]r[/cyan]  Restart discovery flow", classes="help-item")
            yield Static(
                "[dim]Type feedback to refine the draft[/dim]",
                classes="help-item",
            )

            yield Static(
                "[dim]Press Escape or Enter to close[/dim]",
                classes="help-footer",
            )

    def action_dismiss(self) -> None:
        """Close the help screen."""
        self.dismiss(None)
