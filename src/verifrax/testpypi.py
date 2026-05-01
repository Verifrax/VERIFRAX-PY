from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def testpypi_rehearsal_readiness() -> dict[str, Any]:
    manifest_path = ROOT / "TESTPYPI_REHEARSAL.json"
    custody_path = ROOT / "PYPI_CUSTODY.json"
    release_candidate_path = ROOT / "RELEASE_CANDIDATE.json"
    workflow_path = ROOT / ".github/workflows/testpypi-publish.yml"

    missing = [
        str(path.relative_to(ROOT))
        for path in [manifest_path, custody_path, release_candidate_path, workflow_path]
        if not path.exists()
    ]

    refusals: list[str] = []
    if missing:
        refusals.append("TESTPYPI_REHEARSAL_FILE_MISSING")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    custody = json.loads(custody_path.read_text(encoding="utf-8")) if custody_path.exists() else {}
    release_candidate = json.loads(release_candidate_path.read_text(encoding="utf-8")) if release_candidate_path.exists() else {}

    if manifest.get("package") != "verifrax":
        refusals.append("TESTPYPI_PACKAGE_MISMATCH")

    if manifest.get("source_repo") != "Verifrax/VERIFRAX-PY":
        refusals.append("TESTPYPI_SOURCE_REPO_MISMATCH")

    if manifest.get("required_before_production_pypi") is not True:
        refusals.append("TESTPYPI_NOT_REQUIRED_BEFORE_PRODUCTION")

    publisher = manifest.get("publisher", {})
    if publisher.get("method") != "pypi-trusted-publishing":
        refusals.append("TESTPYPI_TRUSTED_PUBLISHING_NOT_BOUND")

    if publisher.get("workflow") != ".github/workflows/testpypi-publish.yml":
        refusals.append("TESTPYPI_WORKFLOW_MISMATCH")

    if publisher.get("environment") != "testpypi":
        refusals.append("TESTPYPI_ENVIRONMENT_MISMATCH")

    if custody.get("release_requirements", {}).get("testpypi_rehearsal_required") is not True:
        refusals.append("PRODUCTION_CUSTODY_DOES_NOT_REQUIRE_TESTPYPI")

    if release_candidate.get("source_repo") != "Verifrax/VERIFRAX-PY":
        refusals.append("RELEASE_CANDIDATE_SOURCE_REPO_MISMATCH")

    return {
        "status": "PASS" if not refusals else "REFUSED",
        "accepted": not refusals,
        "gate": "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "testpypi_project": "verifrax",
        "missing_files": missing,
        "blocking_refusals": refusals,
        "required_before_production_pypi": manifest.get("required_before_production_pypi"),
    }
