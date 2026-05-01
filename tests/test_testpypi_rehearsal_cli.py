from typer.testing import CliRunner

from verifrax.cli import app


def test_self_testpypi_readiness_cli():
    result = CliRunner().invoke(app, ["self", "testpypi-readiness"])
    assert result.exit_code == 0
    assert "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY" in result.output
    assert "\"accepted\": true" in result.output
    assert "Verifrax/VERIFRAX-PY" in result.output
