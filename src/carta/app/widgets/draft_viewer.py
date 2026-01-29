"""Draft viewer widget for displaying and acting on drafts."""

from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical

from carta.app.messages import DraftAction


class DraftViewer(Widget):
    """Widget for displaying a draft document with action options.

    Shows the draft content and available actions (approve, refine, restart, quit).
    Emits DraftAction when user takes an action.
    """

    DEFAULT_CSS = """
    DraftViewer {
        width: 100%;
        height: auto;
        padding: 1;
    }

    DraftViewer .draft-header {
        text-style: bold;
        color: $success;
        margin-bottom: 1;
    }

    DraftViewer .draft-content {
        margin-bottom: 1;
    }

    DraftViewer .draft-options {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def __init__(self, content: str, title: str = "Discovery Document Draft") -> None:
        super().__init__()
        self._content = content
        self._title = title

    def compose(self) -> ComposeResult:
        """Compose the draft display."""
        with Vertical():
            yield Static(
                f"[bold green]━━━ {self._title} ━━━[/bold green]",
                classes="draft-header",
            )
            yield Static(self._content, classes="draft-content")
            yield Static(
                "[dim]Type 'approve' to accept and save, 'new' to start over, "
                "'quit' to exit, or provide feedback to refine.[/dim]",
                classes="draft-options",
            )

    @property
    def content(self) -> str:
        """Get the draft content."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Update the draft content."""
        self._content = value
        # Update the Static widget if mounted
        try:
            content_widget = self.query_one(".draft-content", Static)
            content_widget.update(value)
        except Exception:
            pass

    def handle_action(self, value: str) -> bool:
        """Process user input and emit appropriate DraftAction.

        Args:
            value: User input string

        Returns:
            True if action was recognized, False if treated as feedback
        """
        value_lower = value.lower().strip()

        if value_lower in ("approve", "accept", "done", "y", "yes", "a"):
            self.post_message(DraftAction(action="approve"))
            return True
        elif value_lower in ("new", "restart", "again"):
            self.post_message(DraftAction(action="restart"))
            return True
        elif value_lower in ("quit", "exit", "q"):
            self.post_message(DraftAction(action="quit"))
            return True
        else:
            # Treat as refinement feedback
            self.post_message(DraftAction(action="refine", feedback=value))
            return False
