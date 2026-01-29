"""Custom Textual messages for inter-component communication."""

from textual.message import Message


class AgentProgress(Message):
    """Emitted when agent makes a tool call."""

    def __init__(self, tool_name: str, args: dict, tokens: int) -> None:
        super().__init__()
        self.tool_name = tool_name
        self.args = args
        self.tokens = tokens


class AgentComplete(Message):
    """Emitted when agent finishes running."""

    def __init__(self, response: dict) -> None:
        super().__init__()
        self.response = response


class PromptSubmitted(Message):
    """Emitted when user submits input from PromptInput widget."""

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value


class QuestionAnswered(Message):
    """Emitted when user selects an option in QuestionSelector."""

    def __init__(self, question_idx: int, option_idx: int) -> None:
        super().__init__()
        self.question_idx = question_idx
        self.option_idx = option_idx


class DraftAction(Message):
    """Emitted when user takes an action on the draft."""

    def __init__(self, action: str, feedback: str = "") -> None:
        super().__init__()
        self.action = action  # "approve", "refine", "restart", "quit"
        self.feedback = feedback


class FeatureSelected(Message):
    """Emitted when user selects a feature from the list."""

    def __init__(self, feature_path: str, discovery_content: str) -> None:
        super().__init__()
        self.feature_path = feature_path
        self.discovery_content = discovery_content


class MenuSelected(Message):
    """Emitted when user selects an option from home menu."""

    def __init__(self, option: str) -> None:
        super().__init__()
        self.option = option  # "discovery", "plan", "quit"
