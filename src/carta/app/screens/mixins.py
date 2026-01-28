"""Mixins for screen classes."""

from typing import TYPE_CHECKING, Any, cast

from textual.widgets import LoadingIndicator

from carta.app.widgets.agent_output import AgentOutput
from carta.app.widgets.prompt_input import PromptInput

if TYPE_CHECKING:
    pass


class AgentScreenMixin:
    """Mixin providing agent output helpers for screens that run agents.

    Provides common functionality for screens that display agent output,
    loading indicators, and prompt input.

    Note: This mixin is designed to be used with Screen subclasses.
    """

    def query_one(self, selector: str, expect_type: type | None = None) -> Any:
        """Placeholder for Screen.query_one - implemented by Screen."""
        raise NotImplementedError

    @property
    def output(self) -> AgentOutput:
        """Get the output widget."""
        return cast(AgentOutput, self.query_one("#output", AgentOutput))

    @property
    def prompt(self) -> PromptInput:
        """Get the prompt input widget."""
        return cast(PromptInput, self.query_one("#prompt-container", PromptInput))

    def write_output(self, text: str) -> None:
        """Write text to the output log."""
        self.output.write(text)

    def clear_output(self) -> None:
        """Clear the output log."""
        self.output.clear()

    def show_loading(self) -> None:
        """Show loading indicator and disable input."""
        loading = cast(LoadingIndicator, self.query_one("#loading", LoadingIndicator))
        loading.remove_class("hidden")
        self.prompt.disabled = True

    def hide_loading(self) -> None:
        """Hide loading indicator and enable input."""
        loading = cast(LoadingIndicator, self.query_one("#loading", LoadingIndicator))
        loading.add_class("hidden")
        self.prompt.disabled = False
        self.prompt.focus()

    def set_placeholder(self, text: str) -> None:
        """Update the input placeholder text."""
        self.prompt.placeholder = text
