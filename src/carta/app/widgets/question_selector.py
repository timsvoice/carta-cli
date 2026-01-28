"""Question selector widget for wizard Q&A."""

from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical

from carta.app.messages import QuestionAnswered


class QuestionSelector(Widget):
    """Widget for displaying a question with numbered options.

    Shows progress bar, question text, and selectable options.
    Emits QuestionAnswered when an option is selected.
    """

    DEFAULT_CSS = """
    QuestionSelector {
        width: 100%;
        height: auto;
        padding: 1;
    }

    QuestionSelector .question-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    QuestionSelector .question-progress {
        color: $text-muted;
        margin-bottom: 1;
    }

    QuestionSelector .question-text {
        text-style: italic;
        margin-bottom: 1;
    }

    QuestionSelector .option {
        margin-left: 2;
    }

    QuestionSelector .option-selected {
        color: $success;
    }

    QuestionSelector .option-impact {
        color: $text-muted;
        margin-left: 6;
    }
    """

    def __init__(
        self,
        question: dict,
        question_idx: int,
        total_questions: int,
        selected_option: int | None = None,
    ) -> None:
        super().__init__()
        self.question = question
        self.question_idx = question_idx
        self.total_questions = total_questions
        self.selected_option = selected_option

    def compose(self) -> ComposeResult:
        """Compose the question display."""
        idx = self.question_idx
        total = self.total_questions

        # Progress indicator
        progress = "█" * (idx + 1) + "░" * (total - idx - 1)
        percent = int(((idx + 1) / total) * 100)

        with Vertical():
            yield Static(
                f"[bold cyan]Question {idx + 1} of {total}: {self.question['topic']}[/bold cyan]",
                classes="question-header",
            )
            yield Static(f"[dim]{progress} {percent}%[/dim]", classes="question-progress")
            yield Static(
                f"[italic]{self.question['question']}[/italic]",
                classes="question-text",
            )

            # Display options
            for i, opt in enumerate(self.question["options"]):
                prefix = "  "
                option_class = "option"
                if self.selected_option == i:
                    prefix = "[green]✓ [/green]"
                    option_class = "option option-selected"

                yield Static(
                    f"{prefix}[bold]{i + 1}.[/bold] {opt['description']}",
                    classes=option_class,
                )
                yield Static(f"[dim]Impact: {opt['impact']}[/dim]", classes="option-impact")

    def select_option(self, option_idx: int) -> bool:
        """Select an option and emit QuestionAnswered message.

        Args:
            option_idx: 0-based option index

        Returns:
            True if selection was valid, False otherwise
        """
        if 0 <= option_idx < len(self.question["options"]):
            self.selected_option = option_idx
            self.post_message(
                QuestionAnswered(
                    question_idx=self.question_idx,
                    option_idx=option_idx,
                )
            )
            return True
        return False

    def get_option_count(self) -> int:
        """Get the number of options for this question."""
        return len(self.question["options"])

    def get_selected_description(self) -> str | None:
        """Get the description of the selected option."""
        if self.selected_option is not None:
            desc: str = self.question["options"][self.selected_option]["description"]
            return desc
        return None
