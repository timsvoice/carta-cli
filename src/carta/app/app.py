"""Carta TUI application with screen-based architecture."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from carta.app.screens.feature_screen import FeatureScreen
from carta.app.screens.wizard_screen import WizardScreen
from carta.app.screens.draft_screen import DraftScreen
from carta.app.screens.modals import HelpScreen, ConfirmQuitScreen
from carta.app.types import FeatureResult, WizardResult, DraftResult


class CartaApp(App):
    """Main Carta application with screen-based navigation."""

    TITLE = "Carta"
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("question_mark", "show_help", "Help", show=True),
        Binding("q", "request_quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        # Shared state between screens
        self.feature_description: str = ""
        self.wizard_answers: list[dict] = []

    def compose(self) -> ComposeResult:
        """Compose the app shell (screens provide their own layouts)."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Start the discovery flow when the app mounts."""
        self._start_discovery_flow()

    # ─── Screen-Based Flow ───────────────────────────────────────────

    def _start_discovery_flow(self) -> None:
        """Entry point for the discovery workflow using screens."""
        self.feature_description = ""
        self.wizard_answers = []
        self.push_screen(FeatureScreen(), callback=self._on_feature_done)

    def _on_feature_done(self, result: FeatureResult) -> None:
        """Handle FeatureScreen dismiss result."""
        match result.status:
            case "success":
                self.feature_description = result.feature_description
                if result.questions is None:
                    self.notify("No questions returned", severity="error")
                    self._start_discovery_flow()
                    return
                # Transition to wizard screen
                self.push_screen(
                    WizardScreen(result.questions),
                    callback=self._on_wizard_done,
                )
            case "error":
                self.notify(f"Error: {result.error}", severity="error")
                self._start_discovery_flow()

    def _on_wizard_done(self, result: WizardResult) -> None:
        """Handle WizardScreen dismiss result."""
        match result.status:
            case "completed":
                if result.answers is None:
                    self.notify("No answers returned", severity="error")
                    self._start_discovery_flow()
                    return
                self.wizard_answers = result.answers
                # Transition to draft screen
                self.push_screen(
                    DraftScreen(
                        feature_description=self.feature_description,
                        answers=self.wizard_answers,
                    ),
                    callback=self._on_draft_done,
                )
            case "cancelled":
                self._start_discovery_flow()

    def _on_draft_done(self, result: DraftResult) -> None:
        """Handle DraftScreen dismiss result."""
        match result.status:
            case "done":
                self.exit()
            case "restart":
                self._start_discovery_flow()

    # ─── Global Actions ──────────────────────────────────────────────

    def action_show_help(self) -> None:
        """Show help modal screen."""
        self.push_screen(HelpScreen())

    def action_request_quit(self) -> None:
        """Show quit confirmation modal."""
        self.push_screen(ConfirmQuitScreen(), callback=self._on_quit_confirm)

    def _on_quit_confirm(self, confirmed: bool) -> None:
        """Handle quit confirmation result."""
        if confirmed:
            self.exit()


def main():
    app = CartaApp()
    app.run()
