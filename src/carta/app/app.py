"""Carta TUI application with handler-based architecture."""

from pathlib import Path
from threading import Thread
from typing import Callable

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, LoadingIndicator
from textual.containers import Container

from carta.app.handlers.base import BaseHandler
from carta.app.handlers.feature import FeatureHandler
from carta.app.handlers.wizard import WizardHandler
from carta.app.handlers.draft import DraftHandler
from carta.app.types import FeatureResult, WizardResult, DraftResult


class CartaApp(App):
    """Main Carta application - owns all UI and delegates input to handlers."""

    TITLE = "Carta"
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def __init__(self):
        super().__init__()
        # Shared state between handlers
        self.feature_description: str = ""
        self.wizard_answers: list[dict] = []
        # Current input handler
        self._current_handler: BaseHandler | None = None

    def compose(self) -> ComposeResult:
        """Compose the single, persistent UI layout."""
        yield Header()
        yield RichLog(id="output", highlight=True, markup=True, wrap=True)
        yield LoadingIndicator(id="loading", classes="hidden")
        yield Container(
            Input(placeholder="", id="user-input"),
            id="input-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start the discovery flow when the app mounts."""
        self._start_discovery_flow()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Route input to the current handler."""
        value = event.value.strip()
        if not value:
            return

        self.query_one("#user-input", Input).value = ""

        if self._current_handler:
            self._current_handler.handle_input(value)

    # ─── Helper Methods for Handlers ────────────────────────────────

    def write_output(self, text: str) -> None:
        """Write text to the output log."""
        self.query_one("#output", RichLog).write(text)

    def show_loading(self) -> None:
        """Show loading indicator and disable input."""
        self.query_one("#loading", LoadingIndicator).remove_class("hidden")
        self.query_one("#user-input", Input).disabled = True

    def hide_loading(self) -> None:
        """Hide loading indicator and enable input."""
        self.query_one("#loading", LoadingIndicator).add_class("hidden")
        user_input = self.query_one("#user-input", Input)
        user_input.disabled = False
        user_input.focus()

    def set_placeholder(self, text: str) -> None:
        """Update the input placeholder text."""
        self.query_one("#user-input", Input).placeholder = text

    def run_agent_task(self, task: Callable[[], None]) -> None:
        """Run a task in a background thread."""
        thread = Thread(target=task, daemon=True)
        thread.start()

    # ─── Handler Management ─────────────────────────────────────────

    def _set_handler(self, handler: BaseHandler) -> None:
        """Set the current handler and start it."""
        self._current_handler = handler
        handler.start()

    # ─── Discovery Flow Orchestration ───────────────────────────────

    def _start_discovery_flow(self) -> None:
        """Entry point for the discovery workflow."""
        self.feature_description = ""
        self.wizard_answers = []
        self._set_handler(FeatureHandler(self, self._on_feature_result))

    def _on_feature_result(self, result: FeatureResult) -> None:
        """Handle feature handler completion."""
        match result.status:
            case "success":
                self.feature_description = result.feature_description
                if result.questions is None:
                    self.notify("No questions returned", severity="error")
                    self._start_discovery_flow()
                    return
                self._set_handler(WizardHandler(self, self._on_wizard_result, result.questions))
            case "error":
                self.notify(f"Error: {result.error}", severity="error")
                self._start_discovery_flow()

    def _on_wizard_result(self, result: WizardResult) -> None:
        """Handle wizard handler completion."""
        match result.status:
            case "completed":
                if result.answers is None:
                    self.notify("No answers returned", severity="error")
                    self._start_discovery_flow()
                    return
                self.wizard_answers = result.answers
                self._set_handler(
                    DraftHandler(
                        self,
                        self._on_draft_result,
                        feature_description=self.feature_description,
                        answers=self.wizard_answers,
                    )
                )
            case "cancelled":
                self._start_discovery_flow()

    def _on_draft_result(self, result: DraftResult) -> None:
        """Handle draft handler completion."""
        match result.status:
            case "done":
                self.exit()
            case "restart":
                # Clear the output for a fresh start
                self.query_one("#output", RichLog).clear()
                self._start_discovery_flow()


def main():
    app = CartaApp()
    app.run()
