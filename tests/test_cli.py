"""Tests for `kune` package."""

from kune import cli

def test_command_line_interface(cli_runner):
    """Test the CLI."""
    result = cli_runner.invoke(cli.main)
    assert result.exit_code == 2
    assert "Error: Missing argument 'HTML_FILE'." in result.output
    
def test_cli_help(cli_runner):
    help_result = cli_runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output
