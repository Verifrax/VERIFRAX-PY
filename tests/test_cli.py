from typer.testing import CliRunner
from verifrax.cli import app


def test_doctor():
    result = CliRunner().invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "python-sdk-cli-implementation" in result.output
