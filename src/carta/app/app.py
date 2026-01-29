"""Carta TUI application with screen-based architecture."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from carta.app.screens.feature_screen import FeatureScreen
from carta.app.screens.wizard_screen import WizardScreen
from carta.app.screens.draft_screen import DraftScreen
from carta.app.screens.home_screen import HomeScreen
from carta.app.screens.plan_select_screen import PlanSelectScreen
from carta.app.screens.plan_wizard_screen import PlanWizardScreen
from carta.app.screens.plan_draft_screen import PlanDraftScreen
from carta.app.screens.modals import HelpScreen, ConfirmQuitScreen, ConfirmPlanPromptScreen
from carta.app.types import (
    FeatureResult,
    WizardResult,
    DraftResult,
    HomeResult,
    PlanSelectResult,
    PlanWizardResult,
    PlanDraftResult,
)


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
        # Shared state for discovery flow
        self.feature_description: str = ""
        self.wizard_answers: list[dict] = []
        # Shared state for plan flow
        self._plan_discovery_content: str = ""
        self._plan_feature_path: str = ""
        self._plan_answers: list[dict] = []
        # Track last saved feature for post-discovery prompt
        self._last_saved_feature_path: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the app shell (screens provide their own layouts)."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Start with home screen when the app mounts."""
        self._show_home()

    # ─── Home Screen ──────────────────────────────────────────────────

    def _show_home(self) -> None:
        """Show the home menu screen."""
        self.push_screen(HomeScreen(), callback=self._on_home_done)

    def _on_home_done(self, result: HomeResult) -> None:
        """Handle HomeScreen dismiss result."""
        match result.status:
            case "discovery":
                self._start_discovery_flow()
            case "plan":
                self._start_plan_flow()
            case "quit":
                self.exit()

    # ─── Discovery Flow ───────────────────────────────────────────────

    def _start_discovery_flow(self) -> None:
        """Entry point for the discovery workflow using screens."""
        self.feature_description = ""
        self.wizard_answers = []
        self._last_saved_feature_path = None
        self.push_screen(FeatureScreen(), callback=self._on_feature_done)

    def _on_feature_done(self, result: FeatureResult) -> None:
        """Handle FeatureScreen dismiss result."""
        match result.status:
            case "success":
                self.feature_description = result.feature_description
                if result.questions is None:
                    self.notify("No questions returned", severity="error")
                    self._show_home()
                    return
                # Transition to wizard screen
                self.push_screen(
                    WizardScreen(result.questions),
                    callback=self._on_wizard_done,
                )
            case "error":
                self.notify(f"Error: {result.error}", severity="error")
                self._show_home()

    def _on_wizard_done(self, result: WizardResult) -> None:
        """Handle WizardScreen dismiss result."""
        match result.status:
            case "completed":
                if result.answers is None:
                    self.notify("No answers returned", severity="error")
                    self._show_home()
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
                self._show_home()

    def _on_draft_done(self, result: DraftResult) -> None:
        """Handle DraftScreen dismiss result."""
        match result.status:
            case "done":
                # Check if we should prompt for plan creation
                if result.prompt_for_plan and result.feature_path:
                    self._last_saved_feature_path = result.feature_path
                    self.push_screen(
                        ConfirmPlanPromptScreen(),
                        callback=self._on_plan_prompt_done,
                    )
                else:
                    self._show_home()
            case "restart":
                self._start_discovery_flow()

    def _on_plan_prompt_done(self, continue_to_plan: bool) -> None:
        """Handle plan prompt confirmation."""
        if continue_to_plan and self._last_saved_feature_path:
            # Start plan flow with the just-saved feature pre-selected
            self._start_plan_flow(preselect_path=self._last_saved_feature_path)
        else:
            self._show_home()

    # ─── Plan Flow ────────────────────────────────────────────────────

    def _start_plan_flow(self, preselect_path: str | None = None) -> None:
        """Entry point for the plan workflow."""
        self._plan_discovery_content = ""
        self._plan_feature_path = ""
        self._plan_answers = []
        self.push_screen(
            PlanSelectScreen(preselect_path=preselect_path),
            callback=self._on_plan_select_done,
        )

    def _on_plan_select_done(self, result: PlanSelectResult) -> None:
        """Handle PlanSelectScreen dismiss result."""
        match result.status:
            case "selected":
                if result.feature_path is None or result.discovery_content is None:
                    self.notify("No feature selected", severity="error")
                    self._show_home()
                    return
                self._plan_feature_path = result.feature_path
                self._plan_discovery_content = result.discovery_content
                # Transition to plan wizard screen
                self.push_screen(
                    PlanWizardScreen(result.discovery_content),
                    callback=self._on_plan_wizard_done,
                )
            case "cancelled":
                self._show_home()

    def _on_plan_wizard_done(self, result: PlanWizardResult) -> None:
        """Handle PlanWizardScreen dismiss result."""
        match result.status:
            case "completed":
                if result.answers is None:
                    self.notify("No answers returned", severity="error")
                    self._show_home()
                    return
                self._plan_answers = result.answers
                # Transition to plan draft screen
                self.push_screen(
                    PlanDraftScreen(
                        discovery_content=self._plan_discovery_content,
                        answers=self._plan_answers,
                        feature_path=self._plan_feature_path,
                    ),
                    callback=self._on_plan_draft_done,
                )
            case "cancelled":
                self._show_home()

    def _on_plan_draft_done(self, result: PlanDraftResult) -> None:
        """Handle PlanDraftScreen dismiss result."""
        match result.status:
            case "done":
                self._show_home()
            case "restart":
                self._start_plan_flow()

    # ─── Global Actions ───────────────────────────────────────────────

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
