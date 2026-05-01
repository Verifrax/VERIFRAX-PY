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
    "TESTPYPI_REHEARSAL.json",
    "scripts/check-api-machine-contract-replay-boundary.py",
    "scripts/check-receipt-verdict-projection-replay-boundary.py",
    "scripts/check-terminal-nonrecognition-nonrecourse-guard.py",
    "scripts/check-pypi-custody-attestation-release-gate.py",
    "scripts/check-distribution-installation-replay-proof.py",
    "scripts/check-release-candidate-attestation-readiness-boundary.py",
    "scripts/check-testpypi-rehearsal-attestation-boundary.py",
    "scripts/check-pytest-warning-free-release-gate.py",
]

REQUIRED_GATES = {
    "API_MACHINE_CONTRACT_REPLAY_BOUNDARY",
    "RECEIPT_VERDICT_PROJECTION_REPLAY_BOUNDARY",
    "TERMINAL_NONRECOGNITION_NONRECOURSE_GUARD",
    "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE",
    "DISTRIBUTION_INSTALLATION_REPLAY_PROOF",
    "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
    "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY",
    "PYTEST_WARNING_FREE_RELEASE_GATE",
}


def _load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def release_readiness() -> dict[str, Any]:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]

    candidate = _load_json("RELEASE_CANDIDATE.json") if (ROOT / "RELEASE_CANDIDATE.json").exists() else {}
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

    release_requirements = custody.get("release_requirements", {})
    required_flags = {
        "trusted_publishing_required": "TRUSTED_PUBLISHING_NOT_REQUIRED",
        "attestation_required": "PYPI_ATTESTATION_NOT_REQUIRED",
        "sdist_required": "SDIST_NOT_REQUIRED",
        "wheel_required": "WHEEL_NOT_REQUIRED",
        "release_candidate_readiness_required": "RELEASE_CANDIDATE_READINESS_NOT_REQUIRED",
        "testpypi_rehearsal_required": "TESTPYPI_REHEARSAL_NOT_REQUIRED",
        "pytest_warning_free_required": "PYTEST_WARNING_FREE_NOT_REQUIRED",
        "terminal_nonrecognition_nonrecourse_guard_required": "TERMINAL_GUARD_NOT_REQUIRED",
        "receipt_verdict_projection_replay_required": "PROJECTION_REPLAY_NOT_REQUIRED",
        "api_machine_contract_replay_required": "API_CONTRACT_REPLAY_NOT_REQUIRED",
    }

    for key, code in required_flags.items():
        if release_requirements.get(key) is not True:
            refusals.append(code)

    if package.get("not_sovereignty") is not True:
        refusals.append("PACKAGE_SOVEREIGNTY_OVERCLAIM")

    if package.get("package_truth_subordinate") is not True:
        refusals.append("PACKAGE_TRUTH_OVERCLAIM")

    if terminal.get("rule") != "VERIFICATION_IS_NOT_TERMINAL_RECOGNITION_OR_TERMINAL_RECOURSE":
        refusals.append("TERMINAL_BOUNDARY_RULE_MISSING")

    required_gates = candidate.get("required_gates", [])
    missing_gates = sorted(REQUIRED_GATES.difference(required_gates))
    if missing_gates:
        refusals.append("RELEASE_CANDIDATE_REQUIRED_GATE_MISSING")

    return {
        "status": "PASS" if not refusals else "REFUSED",
        "accepted": not refusals,
        "gate": "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "missing_files": missing,
        "missing_gates": missing_gates,
        "blocking_refusals": refusals,
        "required_gates": required_gates,
    }
