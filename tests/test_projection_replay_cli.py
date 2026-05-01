from typer.testing import CliRunner

from verifrax.cli import app


runner = CliRunner()


def test_receipt_projection_inspect_cli():
    result = runner.invoke(app, ["receipt", "inspect", "examples/receipt-projection-fixture.json"])
    assert result.exit_code == 0
    assert "EXECUTION_RECEIPT_PROJECTION" in result.output
    assert "Verifrax/CORPIFORM" in result.output
    assert "\"accepted\": true" in result.output


def test_verdict_projection_inspect_cli():
    result = runner.invoke(app, ["verdict", "inspect", "examples/verdict-projection-fixture.json"])
    assert result.exit_code == 0
    assert "VERIFICATION_VERDICT_PROJECTION" in result.output
    assert "Verifrax/VERIFRAX" in result.output
    assert "\"accepted\": true" in result.output


def test_incomplete_receipt_projection_refuses_cli():
    result = runner.invoke(app, ["receipt", "inspect", "examples/incomplete-receipt-projection.json"])
    assert result.exit_code == 0
    assert "RECEIPT_PROJECTION_INCOMPLETE" in result.output
    assert "\"accepted\": false" in result.output
