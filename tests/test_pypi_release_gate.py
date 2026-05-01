from pathlib import Path
import json
import tomllib


def test_pypi_custody_requires_trusted_publishing():
    custody = json.loads(Path("PYPI_CUSTODY.json").read_text())
    assert custody["pypi_project"] == "verifrax"
    assert custody["source_repo"] == "Verifrax/VERIFRAX-PY"
    assert custody["publisher"]["method"] == "pypi-trusted-publishing"
    assert custody["publisher"]["oidc_provider"] == "github-actions"
    assert custody["publisher"]["environment"] == "pypi"
    assert custody["release_requirements"]["attestation_required"] is True


def test_pyproject_release_identity():
    data = tomllib.loads(Path("pyproject.toml").read_text())
    assert data["project"]["name"] == "verifrax"
    assert data["project"]["license"] == "Apache-2.0"
    assert data["project"]["scripts"]["verifrax"] == "verifrax.cli:app"


def test_package_boundary_forbids_sovereign_inference():
    boundary = json.loads(Path("PACKAGE_BOUNDARY.json").read_text())
    assert boundary["not_sovereignty"] is True
    assert boundary["package_truth_subordinate"] is True
    assert "python_sdk_decides_terminal_recognition" in boundary["forbidden_inferences"]
    assert "python_sdk_assigns_terminal_recourse" in boundary["forbidden_inferences"]
