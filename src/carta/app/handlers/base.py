"""Base handler protocol for input handling."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from carta.app.app import CartaApp


class BaseHandler(ABC):
    """Abstract base class for input handlers.

    Handlers are pure logic classes that process user input and write to the App's
    shared output. They don't own any UI widgets - the App owns all UI.
    """

    def __init__(self, app: "CartaApp", on_complete: Callable[[Any], None]):
        self.app = app
        self.on_complete = on_complete

    @abstractmethod
    def start(self) -> None:
        """Called when this handler becomes active.

        Use this to set the input placeholder, write initial messages, etc.
        """
        pass

    @abstractmethod
    def handle_input(self, value: str) -> None:
        """Handle user input.

        Args:
            value: The stripped input value from the user.
        """
        pass
