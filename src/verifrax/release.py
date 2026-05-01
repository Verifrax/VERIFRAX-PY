from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


REQUIRED_FILES = [
    "RELEASE_CANDIDATE.json",
    "PYPI_CUSTODY.json",
    "PACKAGE_BOUNDARY.json",
    "SOURCE_BINDINGS.json",
    "TERMINAL_BOUNDARY.json",
    "scripts/check-api-machine-contract-replay-boundary.py",
    "scripts/check-receipt-verdict-projection-replay-boundary.py",
    "scripts/check-terminal-nonrecognition-nonrecourse-guard.py",
    "scripts/check-pypi-custody-attestation-release-gate.py",
    "scripts/check-distribution-installation-replay-proof.py",
]


def _load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def release_readiness() -> dict[str, Any]:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]

    candidate = _load_json("RELEASE_CANDIDATE.json") if not missing or (ROOT / "RELEASE_CANDIDATE.json").exists() else {}
    custody = _load_json("PYPI_CUSTODY.json") if (ROOT / "PYPI_CUSTODY.json").exists() else {}
    package = _load_json("PACKAGE_BOUNDARY.json") if (ROOT / "PACKAGE_BOUNDARY.json").exists() else {}
    terminal = _load_json("TERMINAL_BOUNDARY.json") if (ROOT / "TERMINAL_BOUNDARY.json").exists() else {}

    refusals: list[str] = []

    if missing:
        refusals.append("RELEASE_READINESS_FILE_MISSING")

    if candidate.get("package") != "verifrax":
        refusals.append("RELEASE_CANDIDATE_PACKAGE_MISMATCH")

    if candidate.get("version") != "0.1.0":
        refusals.append("RELEASE_CANDIDATE_VERSION_MISMATCH")

    if candidate.get("source_repo") != "Verifrax/VERIFRAX-PY":
        refusals.append("RELEASE_CANDIDATE_SOURCE_REPO_MISMATCH")

    if custody.get("publisher", {}).get("method") != "pypi-trusted-publishing":
        refusals.append("TRUSTED_PUBLISHING_NOT_BOUND")

    if custody.get("release_requirements", {}).get("attestation_required") is not True:
        refusals.append("PYPI_ATTESTATION_NOT_REQUIRED")

    if package.get("truth_owner") is True or package.get("not_sovereignty") is not True:
        refusals.append("PACKAGE_SOVEREIGNTY_OVERCLAIM")

    if terminal.get("rule") != "VERIFICATION_IS_NOT_TERMINAL_RECOGNITION_OR_TERMINAL_RECOURSE":
        refusals.append("TERMINAL_BOUNDARY_RULE_MISSING")

    return {
        "status": "PASS" if not refusals else "REFUSED",
        "accepted": not refusals,
        "gate": "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "missing_files": missing,
        "blocking_refusals": refusals,
        "required_gates": candidate.get("required_gates", []),
    }
