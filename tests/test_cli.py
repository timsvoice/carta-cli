from carta.cli import cli


def test_cli_help(cli_runner):
    """CLI shows help text."""
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Carta CLI" in result.output


def test_cli_no_args_shows_usage(cli_runner):
    """CLI without arguments shows usage info."""
    result = cli_runner.invoke(cli)
    assert "Usage:" in result.output or "Carta CLI" in result.output
