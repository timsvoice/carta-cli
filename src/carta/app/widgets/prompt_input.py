"""Prompt input widget - Elia-style TextArea with border title."""

from textual.widgets import TextArea
from textual.binding import Binding
from textual import on

from carta.app.messages import PromptSubmitted


class PromptInput(TextArea):
    """TextArea-based prompt input with border title.

    Emits PromptSubmitted message when user submits input.
    Uses Elia-style border title for the label.
    """

    DEFAULT_CSS = """
    PromptInput {
        height: auto;
        max-height: 50%;
        dock: bottom;
        margin: 0;
    }
    """

    BINDINGS = [
        Binding("ctrl+j", "submit_prompt", "Send", key_display="^j"),
    ]

    def __init__(
        self,
        label: str = "Enter your message...",
        id: str | None = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(id=id, language="markdown")
        self._label = label
        self._placeholder = placeholder

    def on_mount(self) -> None:
        """Set up border title on mount."""
        self.border_title = self._label

    @property
    def label(self) -> str:
        """Get the current label (border title)."""
        return str(self.border_title) if self.border_title else ""

    @label.setter
    def label(self, value: str) -> None:
        """Set the label (border title)."""
        self.border_title = value

    @property
    def placeholder(self) -> str:
        """Get placeholder (not used with TextArea, kept for compatibility)."""
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        """Set placeholder (updates border title instead)."""
        self._placeholder = value

    @on(TextArea.Changed)
    def on_text_changed(self, _event: TextArea.Changed) -> None:
        """Update border subtitle when text changes."""
        if self.text.strip():
            self.border_subtitle = "[white]^j[/] Send"
        else:
            self.border_subtitle = ""

    def action_submit_prompt(self) -> None:
        """Submit the prompt."""
        text = self.text.strip()
        if not text:
            return

        self.clear()
        self.post_message(PromptSubmitted(text))

    def on_key(self, event) -> None:
        """Handle key events."""
        # Allow Enter to submit if single line, otherwise require ctrl+j
        if event.key == "enter" and "\n" not in self.text:
            event.prevent_default()
            self.action_submit_prompt()
