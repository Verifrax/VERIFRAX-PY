import json
from pathlib import Path


def test_pypi_trusted_publisher_readiness_seal_exists():
    data = json.loads(Path("PYPI_TRUSTED_PUBLISHER_READINESS.json").read_text())
    assert data["package"] == "verifrax"
    assert data["do_not_publish"] is True
    assert data["testpypi"]["owner"] == "Verifrax"
    assert data["testpypi"]["repository"] == "VERIFRAX-PY"
    assert data["testpypi"]["workflow_filename"] == "testpypi-publish.yml"
    assert data["testpypi"]["environment"] == "testpypi"
    assert data["pypi"]["owner"] == "Verifrax"
    assert data["pypi"]["repository"] == "VERIFRAX-PY"
    assert data["pypi"]["workflow_filename"] == "pypi-publish.yml"
    assert data["pypi"]["environment"] == "pypi"


def test_publish_workflows_are_manual_oidc_environment_bound():
    testpypi = Path(".github/workflows/testpypi-publish.yml").read_text()
    pypi = Path(".github/workflows/pypi-publish.yml").read_text()

    assert "workflow_dispatch" in testpypi
    assert "id-token: write" in testpypi
    assert "environment: testpypi" in testpypi
    assert "repository-url: https://test.pypi.org/legacy/" in testpypi

    assert "workflow_dispatch" in pypi
    assert "id-token: write" in pypi
    assert "environment: pypi" in pypi
    assert "repository-url: https://test.pypi.org/legacy/" not in pypi


def test_pypi_trusted_publisher_readiness_gate_exists():
    script = Path("scripts/check-pypi-trusted-publisher-readiness-seal.py")
    assert script.exists()
    text = script.read_text()
    assert "PYPI_TRUSTED_PUBLISHER_READINESS_SEAL" in text
    assert "repo:Verifrax/VERIFRAX-PY:environment:testpypi" in text
    assert "repo:Verifrax/VERIFRAX-PY:environment:pypi" in text
    assert "do_not_publish" in text
