"""Base screen with shared compose pattern."""

from typing import Generic, TypeVar

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, LoadingIndicator
from textual.containers import Container

# Type variable for screen result type
ResultT = TypeVar("ResultT")


class BaseScreen(Screen[ResultT], Generic[ResultT]):
    """Base screen with common layout: Header, RichLog, LoadingIndicator, Input, Footer."""

    def __init__(self, input_placeholder: str = ""):
        super().__init__()
        self._input_placeholder = input_placeholder

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="output", highlight=True, markup=True, wrap=True)
        yield LoadingIndicator(id="loading", classes="hidden")
        yield Container(
            Input(placeholder=self._input_placeholder, id="user-input"),
            id="input-container",
        )
        yield Footer()

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

    def write_output(self, text: str) -> None:
        """Write text to the output log."""
        self.query_one("#output", RichLog).write(text)

    def set_placeholder(self, text: str) -> None:
        """Update the input placeholder text."""
        self.query_one("#user-input", Input).placeholder = text
