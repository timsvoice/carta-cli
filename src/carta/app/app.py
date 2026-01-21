"""Carta TUI application with screen-based architecture."""

from pathlib import Path

from textual.app import App

from carta.app.screens.feature import FeatureScreen
from carta.app.screens.wizard import WizardScreen
from carta.app.screens.draft import DraftScreen
from carta.app.types import FeatureResult, WizardResult, DraftResult


class CartaApp(App):
    """Main Carta application - orchestrates screen flow."""

    TITLE = "Carta"
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def __init__(self):
        super().__init__()
        # Shared state between screens
        self.feature_description: str = ""
        self.wizard_answers: list[dict] = []

    def on_mount(self) -> None:
        """Start the discovery flow when the app mounts."""
        self._start_discovery_flow()

    # ─── Discovery Flow Orchestration ───────────────────────────────

    def _start_discovery_flow(self) -> None:
        """Entry point for the discovery workflow."""
        self.feature_description = ""
        self.wizard_answers = []
        self.push_screen(FeatureScreen(), callback=self._on_feature_result)

    def _on_feature_result(self, result: FeatureResult) -> None:
        """Handle feature screen completion."""
        match result.status:
            case "success":
                self.feature_description = result.feature_description
                if result.questions is None:
                    self.notify("No questions returned", severity="error")
                    self._start_discovery_flow()
                    return
                self.push_screen(
                    WizardScreen(result.questions),
                    callback=self._on_wizard_result,
                )
            case "error":
                self.notify(f"Error: {result.error}", severity="error")
                self._start_discovery_flow()

    def _on_wizard_result(self, result: WizardResult) -> None:
        """Handle wizard screen completion."""
        match result.status:
            case "completed":
                if result.answers is None:
                    self.notify("No answers returned", severity="error")
                    self._start_discovery_flow()
                    return
                self.wizard_answers = result.answers
                self.push_screen(
                    DraftScreen(
                        feature_description=self.feature_description,
                        answers=self.wizard_answers,
                    ),
                    callback=self._on_draft_result,
                )
            case "cancelled":
                self._start_discovery_flow()

    def _on_draft_result(self, result: DraftResult) -> None:
        """Handle draft screen completion."""
        match result.status:
            case "done":
                self.exit()
            case "restart":
                self._start_discovery_flow()


def main():
    app = CartaApp()
    app.run()
