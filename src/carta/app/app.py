import json

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, LoadingIndicator
from textual.containers import Container
from textual.worker import get_current_worker
from textual import work

from carta.agent import Agent
from pathlib import Path

_prompts_dir = Path(__file__).parent.parent / "prompts" / "discover"


class CartaApp(App):
    TITLE = "Carta"

    CSS = """
        #output {
            height: 1fr;
            border: solid $primary;
            margin: 0 1;
        }

        #input-container {
            height: 3;
            dock: bottom;
            border: solid $primary;
            margin: 0 1 1 1;
            padding: 0 1;
        }

        #user-input {
            border: none;
            padding: 0;
        }

        #loading {
            dock: bottom;
            height: 1;
            margin: 0 2;
        }

        #loading.hidden {
            display: none;
        }
    """

    def __init__(self):
        super().__init__()
        self.feature_description: str = ""
        self.questions: list[dict] = []
        self.current_question_idx: int = 0
        self.answers: dict[int, int] = {}
        self.wizard_active: bool = False
        self.current_phase: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="output", highlight=True, markup=True, wrap=True)
        yield LoadingIndicator(id="loading", classes="hidden")
        yield Container(
            Input(placeholder="Describe your feature...", id="user-input"),
            id="input-container",
        )
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in the input field."""
        value = event.value.strip()
        if not value:
            return

        self.query_one("#user-input", Input).value = ""

        if self.wizard_active:
            self._handle_wizard_input(value)
        else:
            self._handle_feature_input(value)

    def _handle_feature_input(self, user_message: str) -> None:
        """Handle initial feature description input."""
        output = self.query_one("#output", RichLog)
        user_input = self.query_one("#user-input", Input)
        loading = self.query_one("#loading", LoadingIndicator)

        self.feature_description = user_message

        output.write(f"\n[bold]Feature:[/bold] {user_message}")
        output.write("[dim]Gathering requirements from codebase...[/dim]")

        # Disable input and show loading indicator
        user_input.disabled = True
        loading.remove_class("hidden")
        self.current_phase = "gather"

        # Run agent in background worker
        self._run_gather_agent(user_message)

    @work(thread=True)
    def _run_gather_agent(self, user_message: str) -> dict:
        """Run the gather agent in a background thread."""
        worker = get_current_worker()

        def on_tool_call(tool_name: str, args: dict) -> None:
            if worker.is_cancelled:
                return
            self.call_from_thread(self._on_tool_call, tool_name, args)

        agent = Agent(on_tool_call=on_tool_call)
        system_prompt = (_prompts_dir / "gather.md").read_text()

        response = agent.run(
            f"""
            {system_prompt}
            ## Feature Description
            {user_message}
            """
        )

        if not worker.is_cancelled:
            self.call_from_thread(self._on_gather_complete, response)

        return response

    def _on_tool_call(self, tool_name: str, args: dict) -> None:
        """Display tool call feedback in the UI."""
        output = self.query_one("#output", RichLog)

        if tool_name == "file_read":
            path = args.get("path", "unknown")
            output.write(f"  [dim]> Reading {path}[/dim]")
        elif tool_name == "list_files":
            path = args.get("path", ".")
            output.write(f"  [dim]> Listing {path}[/dim]")

    def _on_gather_complete(self, response: dict) -> None:
        """Handle gather agent completion on main thread."""
        output = self.query_one("#output", RichLog)
        user_input = self.query_one("#user-input", Input)
        loading = self.query_one("#loading", LoadingIndicator)

        # Hide loading and re-enable input
        loading.add_class("hidden")
        user_input.disabled = False
        user_input.focus()

        content = response.get("message", {}).get("content", "")
        questions = self._parse_questions(content)

        if questions:
            self.questions = questions
            self.current_question_idx = 0
            self.answers = {}
            self.wizard_active = True
            output.write(f"[green]Found {len(questions)} questions to clarify.[/green]\n")
            self._display_current_question()
        else:
            output.write("[red]Failed to parse questions from response.[/red]")
            output.write(f"[dim]Raw response: {content}[/dim]")

    def _handle_wizard_input(self, value: str) -> None:
        """Handle option selection during wizard."""
        output = self.query_one("#output", RichLog)
        question = self.questions[self.current_question_idx]

        # Check for navigation commands
        if value.lower() in ("p", "prev", "previous") and self.current_question_idx > 0:
            self.current_question_idx -= 1
            self._display_current_question()
            return

        if value.lower() in ("q", "quit"):
            self._cancel_wizard()
            return

        # Try to parse as option number
        try:
            option_idx = int(value) - 1  # Convert 1-based to 0-based
            if 0 <= option_idx < len(question["options"]):
                self._select_option(option_idx)
            else:
                output.write(
                    f"[yellow]Please enter a number between 1 and {len(question['options'])}[/yellow]"
                )
        except ValueError:
            output.write(
                "[yellow]Enter a number to select an option, 'p' for previous, or 'q' to quit[/yellow]"
            )

    def _display_current_question(self) -> None:
        """Display the current question with options."""
        output = self.query_one("#output", RichLog)
        user_input = self.query_one("#user-input", Input)

        question = self.questions[self.current_question_idx]
        total = len(self.questions)
        idx = self.current_question_idx

        # Progress indicator
        progress = "█" * (idx + 1) + "░" * (total - idx - 1)
        percent = int(((idx + 1) / total) * 100)

        output.write(f"[bold cyan]Question {idx + 1} of {total}: {question['topic']}[/bold cyan]")
        output.write(f"[dim]{progress} {percent}%[/dim]\n")
        output.write(f"[italic]{question['question']}[/italic]\n")

        # Display options
        for i, opt in enumerate(question["options"]):
            prefix = "  "
            # Show checkmark if previously answered
            if self.answers.get(idx) == i:
                prefix = "[green]✓ [/green]"
            output.write(f"{prefix}[bold]{i + 1}.[/bold] {opt['description']}")
            output.write(f"      [dim]Impact: {opt['impact']}[/dim]")

        output.write("")

        # Update input placeholder
        user_input.placeholder = (
            f"Select option (1-{len(question['options'])}), 'p' previous, 'q' quit"
        )

    def _select_option(self, option_idx: int) -> None:
        """Record selection and advance to next question."""
        output = self.query_one("#output", RichLog)
        question = self.questions[self.current_question_idx]
        selected = question["options"][option_idx]

        self.answers[self.current_question_idx] = option_idx
        output.write(f"[green]→ Selected: {selected['description']}[/green]\n")

        # Advance to next question or complete
        if self.current_question_idx < len(self.questions) - 1:
            self.current_question_idx += 1
            self._display_current_question()
        else:
            self._complete_wizard()

    def _complete_wizard(self) -> None:
        """Complete the wizard and run draft agent."""
        output = self.query_one("#output", RichLog)
        user_input = self.query_one("#user-input", Input)
        loading = self.query_one("#loading", LoadingIndicator)

        self.wizard_active = False
        self.wizard_results = self._build_results()

        output.write("[bold green]━━━ Requirements Gathered ━━━[/bold green]\n")

        for q in self.wizard_results:
            output.write(f"[bold]{q['topic']}:[/bold] {q.get('answer', 'No answer')}")

        output.write("\n[dim]Drafting discovery document...[/dim]")

        # Disable input and show loading for draft phase
        user_input.disabled = True
        loading.remove_class("hidden")
        self.current_phase = "draft"

        # Run draft agent
        self._run_draft_agent()

    @work(thread=True)
    def _run_draft_agent(self) -> dict:
        """Run the draft agent in a background thread."""
        worker = get_current_worker()

        def on_tool_call(tool_name: str, args: dict) -> None:
            if worker.is_cancelled:
                return
            self.call_from_thread(self._on_tool_call, tool_name, args)

        agent = Agent(on_tool_call=on_tool_call)
        system_prompt = (_prompts_dir / "draft.md").read_text()

        # Format Q&A for the prompt
        qa_text = self._format_qa_for_prompt()

        response = agent.run(
            f"""
            {system_prompt}

            ## Feature Description
            {self.feature_description}

            ## Questions and Answers
            {qa_text}
            """
        )

        if not worker.is_cancelled:
            self.call_from_thread(self._on_draft_complete, response)

        return response

    def _format_qa_for_prompt(self) -> str:
        """Format questions and answers for the draft prompt."""
        lines = []
        for q in self.wizard_results:
            lines.append(f"### {q['topic']}")
            lines.append(f"**Question:** {q['question']}")
            answer = q.get("answer", "No answer provided")
            # Find the impact for the selected answer
            impact = ""
            for opt in q["options"]:
                if opt["description"] == answer:
                    impact = opt["impact"]
                    break
            lines.append(f"**Answer:** {answer}")
            if impact:
                lines.append(f"**Impact:** {impact}")
            lines.append("")
        return "\n".join(lines)

    def _on_draft_complete(self, response: dict) -> None:
        """Handle draft agent completion."""
        output = self.query_one("#output", RichLog)
        user_input = self.query_one("#user-input", Input)
        loading = self.query_one("#loading", LoadingIndicator)

        # Hide loading and re-enable input
        loading.add_class("hidden")
        user_input.disabled = False
        user_input.focus()

        content = response.get("message", {}).get("content", "")

        output.write("\n[bold green]━━━ Discovery Document Draft ━━━[/bold green]\n")
        output.write(content)
        output.write("\n[dim]Draft complete.[/dim]")
        user_input.placeholder = "Describe your feature..."

    def _cancel_wizard(self) -> None:
        """Cancel the wizard."""
        output = self.query_one("#output", RichLog)
        user_input = self.query_one("#user-input", Input)

        self.wizard_active = False
        self.questions = []
        self.answers = {}

        output.write("[yellow]Wizard cancelled.[/yellow]\n")
        user_input.placeholder = "Describe your feature..."

    def _build_results(self) -> list[dict]:
        """Build output with answers included."""
        results = []
        for idx, question in enumerate(self.questions):
            result = question.copy()
            answer_idx = self.answers.get(idx)
            if answer_idx is not None:
                result["answer"] = question["options"][answer_idx]["description"]
            results.append(result)
        return results

    def _parse_questions(self, response: str) -> list[dict] | None:
        """Parse questions JSON from agent response."""
        try:
            result: list[dict] = json.loads(response.strip())
            return result
        except json.JSONDecodeError:
            try:
                start = response.find("[")
                end = response.rfind("]") + 1
                if start != -1 and end > start:
                    result = json.loads(response[start:end])
                    return result
            except json.JSONDecodeError:
                pass
        return None


def main():
    app = CartaApp()
    app.run()
