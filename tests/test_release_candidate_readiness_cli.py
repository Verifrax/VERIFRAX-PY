from typer.testing import CliRunner

from verifrax.cli import app


def test_self_release_readiness_cli():
    result = CliRunner().invoke(app, ["self", "release-readiness"])
    assert result.exit_code == 0
    assert "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY" in result.output
    assert "\"accepted\": true" in result.output
    assert "Verifrax/VERIFRAX-PY" in result.output
