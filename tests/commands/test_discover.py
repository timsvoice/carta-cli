from carta.cli import cli


def test_discover_command_exists(cli_runner):
    """Discover command is registered."""
    result = cli_runner.invoke(cli, ["--help"])
    assert "discover" in result.output


def test_discover_help(cli_runner):
    """Discover command shows help text."""
    result = cli_runner.invoke(cli, ["discover", "--help"])
    assert result.exit_code == 0
    assert "Discover and document requirements" in result.output
