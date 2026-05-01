import json
from pathlib import Path

from verifrax.testpypi import testpypi_rehearsal_readiness


def test_testpypi_rehearsal_manifest():
    data = json.loads(Path("TESTPYPI_REHEARSAL.json").read_text())
    assert data["package"] == "verifrax"
    assert data["source_repo"] == "Verifrax/VERIFRAX-PY"
    assert data["required_before_production_pypi"] is True
    assert data["publisher"]["environment"] == "testpypi"
    assert "production_publish_without_testpypi_rehearsal" in data["forbidden"]


def test_testpypi_rehearsal_readiness_passes():
    result = testpypi_rehearsal_readiness()
    assert result["status"] == "PASS"
    assert result["accepted"] is True
    assert result["blocking_refusals"] == []


def test_testpypi_publish_workflow_uses_oidc_and_testpypi_repository():
    workflow = Path(".github/workflows/testpypi-publish.yml").read_text()
    assert "id-token: write" in workflow
    assert "environment: testpypi" in workflow
    assert "repository-url: https://test.pypi.org/legacy/" in workflow


def test_testpypi_rehearsal_gate_script_exists():
    script = Path("scripts/check-testpypi-rehearsal-attestation-boundary.py")
    assert script.exists()
    text = script.read_text()
    assert "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY" in text
    assert "production_publish_blocked_without_rehearsal" in text
