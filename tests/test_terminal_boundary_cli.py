from typer.testing import CliRunner

from verifrax.cli import app


runner = CliRunner()


def test_terminal_safe_verdict_cli():
    result = runner.invoke(app, ["terminal", "inspect", "examples/terminal-safe-verdict-fixture.json"])
    assert result.exit_code == 0
    assert "VERIFICATION_IS_NOT_RECOGNITION" in result.output
    assert "\"recognition_terminal\": false" in result.output


def test_terminal_overclaim_cli_refuses():
    result = runner.invoke(app, ["terminal", "inspect", "examples/terminal-overclaim-verdict-fixture.json"])
    assert result.exit_code == 0
    assert "TERMINAL_RECOGNITION_OVERCLAIM" in result.output
    assert "TERMINAL_RECOURSE_OVERCLAIM" in result.output
    assert "\"accepted\": false" in result.output
