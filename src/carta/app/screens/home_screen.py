"""Home screen for main menu."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical

from carta.app.widgets.prompt_input import PromptInput
from carta.app.messages import PromptSubmitted
from carta.app.types import HomeResult


class HomeScreen(Screen[HomeResult]):
    """Screen for main menu with discovery/plan options.

    Dismisses with HomeResult indicating user's choice.
    """

    DEFAULT_CSS = """
    HomeScreen {
        layout: vertical;
    }

    HomeScreen #menu-area {
        height: 1fr;
        padding: 2 4;
    }

    HomeScreen .menu-title {
        text-style: bold;
        color: $text;
        margin-bottom: 2;
    }

    HomeScreen .menu-option {
        margin-left: 2;
        margin-bottom: 1;
    }

    HomeScreen .menu-number {
        color: $success;
        text-style: bold;
    }

    HomeScreen .menu-description {
        color: $text-muted;
        margin-left: 4;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        with Vertical(id="menu-area"):
            yield Static("What would you like to do?", classes="menu-title")
            yield Static("[bold green]1.[/bold green] Start Discovery", classes="menu-option")
            yield Static(
                "Create a new feature discovery document",
                classes="menu-description",
            )
            yield Static("[bold green]2.[/bold green] Create Plan", classes="menu-option")
            yield Static(
                "Generate an implementation plan from an existing discovery",
                classes="menu-description",
            )
            yield Static("[bold green]q.[/bold green] Quit", classes="menu-option")
        yield PromptInput(label="Enter choice (1, 2, or q)", id="prompt-container")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the prompt on mount."""
        self.query_one("#prompt-container", PromptInput).focus()

    def on_prompt_submitted(self, event: PromptSubmitted) -> None:
        """Handle prompt submission."""
        value = event.value.strip().lower()

        if value in ("1", "discovery", "d"):
            self.dismiss(HomeResult(status="discovery"))
        elif value in ("2", "plan", "p"):
            self.dismiss(HomeResult(status="plan"))
        elif value in ("q", "quit", "exit"):
            self.dismiss(HomeResult(status="quit"))
        else:
            self.notify("Please enter 1, 2, or q", severity="warning")
