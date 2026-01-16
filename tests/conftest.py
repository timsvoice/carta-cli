import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Provides a Click CliRunner for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def isolated_cli_runner():
    """Provides a CliRunner with an isolated filesystem for tests that create files."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner
