from typer.testing import CliRunner
from verifrax.cli import app

runner = CliRunner()


def test_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "python-sdk-cli-implementation" in result.output


def test_sources():
    result = runner.invoke(app, ["sources"])
    assert result.exit_code == 0
    assert "Verifrax/VERIFRAX-PY" in result.output


def test_policy():
    result = runner.invoke(app, ["policy"])
    assert result.exit_code == 0
    assert "package_default" in result.output


def test_refusal_list():
    result = runner.invoke(app, ["refusal", "list"])
    assert result.exit_code == 0
    assert "OBJECT_CHAIN_INCOMPLETE" in result.output


def test_bundle_inspect():
    result = runner.invoke(app, ["bundle", "inspect", "examples/incomplete-bundle.json"])
    assert result.exit_code == 0
    assert "OBJECT_CHAIN_INCOMPLETE" in result.output
