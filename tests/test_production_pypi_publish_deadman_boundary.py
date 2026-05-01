from pathlib import Path
import json
import subprocess
import sys


def test_production_pypi_publish_authorization_policy_exists():
    data = json.loads(Path("PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_POLICY.json").read_text())
    assert data["package"] == "verifrax"
    assert data["do_not_publish"] is True
    assert data["production_publish_default"] == "REFUSE"
    assert data["authorization_file"] == "PYPI_PRODUCTION_PUBLISH_AUTHORIZATION.json"
    assert data["required_testpypi_live_rehearsal_proof"]["path"] == "evidence/testpypi-live-rehearsal/TESTPYPI_LIVE_REHEARSAL_PROOF.json"


def test_production_pypi_publish_workflow_has_deadman_before_build_and_publish():
    workflow = Path(".github/workflows/pypi-publish.yml").read_text()
    auth = "python scripts/check-production-pypi-publish-authorization-boundary.py"
    build = "python -m build"
    publish = "uses: pypa/gh-action-pypi-publish@release/v1"

    assert "workflow_dispatch" in workflow
    assert "id-token: write" in workflow
    assert "environment: pypi" in workflow
    assert auth in workflow
    assert workflow.index(auth) < workflow.index(build) < workflow.index(publish)


def test_production_pypi_authorization_refuses_by_default():
    completed = subprocess.run(
        [sys.executable, "scripts/check-production-pypi-publish-authorization-boundary.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert completed.returncode != 0
    assert "PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_BOUNDARY" in completed.stdout
    assert "PRODUCTION_PYPI_AUTHORIZATION_MISSING" in completed.stdout


def test_production_pypi_deadman_gate_exists():
    script = Path("scripts/check-production-pypi-publish-deadman-boundary.py")
    assert script.exists()
    text = script.read_text()
    assert "PRODUCTION_PYPI_PUBLISH_DEADMAN_BOUNDARY" in text
    assert "REFUSED_BY_DESIGN" in text
