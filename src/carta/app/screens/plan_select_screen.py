"""Plan selection screen for choosing a feature to create a plan for."""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import ScrollableContainer

from carta.app.widgets.prompt_input import PromptInput
from carta.app.messages import PromptSubmitted
from carta.app.types import PlanSelectResult
from carta.utils.filename import list_feature_directories


class PlanSelectScreen(Screen[PlanSelectResult]):
    """Screen for selecting a feature to create an implementation plan for.

    Lists all features in .carta directory that have discovery.md files.
    Dismisses with PlanSelectResult containing the selected feature path.
    """

    DEFAULT_CSS = """
    PlanSelectScreen {
        layout: vertical;
    }

    PlanSelectScreen #feature-list {
        height: 1fr;
        padding: 1 2;
    }

    PlanSelectScreen .list-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    PlanSelectScreen .feature-item {
        margin-left: 2;
        margin-bottom: 1;
    }

    PlanSelectScreen .feature-number {
        color: $success;
        text-style: bold;
    }

    PlanSelectScreen .no-features {
        color: $warning;
        margin: 2;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, preselect_path: str | None = None) -> None:
        super().__init__()
        self._preselect_path = preselect_path
        self._features: list[Path] = []

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        yield ScrollableContainer(id="feature-list")
        yield PromptInput(label="Select a feature", id="prompt-container")
        yield Footer()

    def on_mount(self) -> None:
        """Load features and display the list."""
        carta_dir = Path(".carta")
        self._features = list_feature_directories(carta_dir)

        container = self.query_one("#feature-list", ScrollableContainer)

        if not self._features:
            container.mount(
                Static(
                    "No discovery documents found in .carta directory.\n"
                    "Run a discovery first to create features.",
                    classes="no-features",
                )
            )
            self.query_one("#prompt-container", PromptInput).label = "Press Escape to go back"
        else:
            container.mount(
                Static("Select a feature to create an implementation plan:", classes="list-title")
            )
            for idx, feature_path in enumerate(self._features, 1):
                container.mount(
                    Static(
                        f"[bold green]{idx}.[/bold green] {feature_path.name}",
                        classes="feature-item",
                    )
                )

            prompt = self.query_one("#prompt-container", PromptInput)
            prompt.label = f"Enter number (1-{len(self._features)}) or 'q' to cancel"

            # If preselecting, auto-select
            if self._preselect_path:
                for idx, fp in enumerate(self._features):
                    if str(fp) == self._preselect_path:
                        self._select_feature(idx)
                        return

        self.query_one("#prompt-container", PromptInput).focus()

    def on_prompt_submitted(self, event: PromptSubmitted) -> None:
        """Handle prompt submission."""
        value = event.value.strip().lower()

        if value in ("q", "quit", "cancel", "back"):
            self._cancel()
            return

        if not self._features:
            self._cancel()
            return

        try:
            idx = int(value) - 1
            if 0 <= idx < len(self._features):
                self._select_feature(idx)
            else:
                self.notify(
                    f"Please enter a number between 1 and {len(self._features)}",
                    severity="warning",
                )
        except ValueError:
            self.notify("Enter a number to select a feature, or 'q' to cancel", severity="warning")

    def action_cancel(self) -> None:
        """Cancel selection."""
        self._cancel()

    def _select_feature(self, idx: int) -> None:
        """Select a feature and dismiss with its details."""
        feature_path = self._features[idx]
        discovery_path = feature_path / "discovery.md"

        try:
            discovery_content = discovery_path.read_text()
        except Exception as e:
            self.notify(f"Error reading discovery.md: {e}", severity="error")
            return

        self.dismiss(
            PlanSelectResult(
                status="selected",
                feature_path=str(feature_path),
                discovery_content=discovery_content,
            )
        )

    def _cancel(self) -> None:
        """Cancel and return to home."""
        self.dismiss(PlanSelectResult(status="cancelled"))
