"""Agent output widget with token counter."""

from textual.widgets import RichLog


class AgentOutput(RichLog):
    """Extended RichLog for displaying agent output with token tracking.

    Provides methods for consistent agent progress feedback display.
    """

    DEFAULT_CSS = """
    AgentOutput {
        height: 1fr;
        border: solid $primary;
        margin: 0 1;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("highlight", True)
        kwargs.setdefault("markup", True)
        kwargs.setdefault("wrap", True)
        super().__init__(*args, **kwargs)
        self._total_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Get total tokens tracked."""
        return self._total_tokens

    def reset_tokens(self) -> None:
        """Reset the token counter."""
        self._total_tokens = 0

    def write_tool_call(self, tool_name: str, args: dict, tokens: int) -> None:
        """Display tool call feedback with consistent formatting.

        Args:
            tool_name: Name of the tool called
            args: Tool arguments (may include _result key)
            tokens: Number of tokens used
        """
        self._total_tokens += tokens
        token_str = f"({tokens:,} tokens)"
        result = args.get("_result", "")
        result_preview = result[:200] + "..." if len(result) > 200 else result
        result_lines = len(result.split("\n"))
        result_chars = len(result)

        if tool_name == "file_read":
            path = args.get("path", "unknown")
            self.write(f"  [dim]> Reading {path} {token_str}[/dim]")
            self.write(f"    [dim]Result: {result_chars} chars, {result_lines} lines[/dim]")
        elif tool_name == "list_files":
            path = args.get("path", ".")
            self.write(f"  [dim]> Listing {path} {token_str}[/dim]")
            self.write(f"    [dim]Result: {result_preview}[/dim]")
        else:
            self.write(f"  [dim]> {tool_name} {token_str}[/dim]")

    def write_tokens_summary(self, total_tokens: int) -> None:
        """Write a token usage summary line."""
        self.write(f"[dim]Total tokens used: {total_tokens:,}[/dim]")

    def write_header(self, text: str) -> None:
        """Write a styled section header."""
        self.write(f"\n[bold green]━━━ {text} ━━━[/bold green]\n")

    def write_status(self, text: str) -> None:
        """Write a dim status message."""
        self.write(f"[dim]{text}[/dim]")

    def write_success(self, text: str) -> None:
        """Write a success message."""
        self.write(f"[green]{text}[/green]")

    def write_error(self, text: str) -> None:
        """Write an error message."""
        self.write(f"[red]{text}[/red]")

    def write_warning(self, text: str) -> None:
        """Write a warning message."""
        self.write(f"[yellow]{text}[/yellow]")
