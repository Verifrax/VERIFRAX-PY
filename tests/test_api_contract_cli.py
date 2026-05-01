from typer.testing import CliRunner

from verifrax.cli import app


def test_api_contract_inspect_cli():
    result = CliRunner().invoke(app, ["api-contract", "inspect", "examples/api-contract-fixture.json"])
    assert result.exit_code == 0
    assert "API" in result.output
    assert "Verifrax/VERIFRAX-API" in result.output
    assert "\"accepted\": true" in result.output
