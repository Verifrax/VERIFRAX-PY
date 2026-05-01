from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_GATES = [
    "API_MACHINE_CONTRACT_REPLAY_BOUNDARY",
    "RECEIPT_VERDICT_PROJECTION_REPLAY_BOUNDARY",
    "TERMINAL_NONRECOGNITION_NONRECOURSE_GUARD",
    "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE",
    "DISTRIBUTION_INSTALLATION_REPLAY_PROOF",
    "PYTEST_WARNING_FREE_RELEASE_GATE",
    "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
    "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY",
]


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def run(cmd: list[str]) -> str:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    ).stdout


def parse_json(output: str, code: str) -> dict:
    stripped = output.strip()
    decoder = json.JSONDecoder()
    for idx, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            obj, end = decoder.raw_decode(stripped[idx:])
        except json.JSONDecodeError:
            continue
        if stripped[idx + end:].strip() == "":
            return obj
    fail(code, output)


def require_file(path: str) -> None:
    if not (ROOT / path).exists():
        fail("RELEASE_REQUIRED_FILE_MISSING", path)


def main() -> None:
    required_files = [
        "RELEASE_CANDIDATE.json",
        "PYPI_CUSTODY.json",
        "PACKAGE_BOUNDARY.json",
        "SOURCE_BINDINGS.json",
        "TERMINAL_BOUNDARY.json",
        "TESTPYPI_REHEARSAL.json",
        ".github/workflows/test.yml",
        ".github/workflows/api-machine-contract-replay-boundary.yml",
        ".github/workflows/receipt-verdict-projection-replay-boundary.yml",
        ".github/workflows/terminal-nonrecognition-nonrecourse-guard.yml",
        ".github/workflows/pypi-release-gate.yml",
        ".github/workflows/distribution-installation-replay-proof.yml",
        ".github/workflows/release-candidate-attestation-readiness-boundary.yml",
        ".github/workflows/testpypi-rehearsal-attestation-boundary.yml",
        ".github/workflows/pytest-warning-free-release-gate.yml",
        ".github/workflows/pypi-publish.yml",
        ".github/workflows/testpypi-publish.yml",
        "scripts/check-api-machine-contract-replay-boundary.py",
        "scripts/check-receipt-verdict-projection-replay-boundary.py",
        "scripts/check-terminal-nonrecognition-nonrecourse-guard.py",
        "scripts/check-pypi-custody-attestation-release-gate.py",
        "scripts/check-distribution-installation-replay-proof.py",
        "scripts/check-release-candidate-attestation-readiness-boundary.py",
        "scripts/check-testpypi-rehearsal-attestation-boundary.py",
        "scripts/check-pytest-warning-free-release-gate.py",
    ]

    for path in required_files:
        require_file(path)

    candidate = json.loads((ROOT / "RELEASE_CANDIDATE.json").read_text(encoding="utf-8"))

    if candidate.get("package") != "verifrax":
        fail("RELEASE_PACKAGE_MISMATCH", json.dumps(candidate, indent=2))
    if candidate.get("version") != "0.1.0":
        fail("RELEASE_VERSION_MISMATCH", json.dumps(candidate, indent=2))
    if candidate.get("source_repo") != "Verifrax/VERIFRAX-PY":
        fail("RELEASE_SOURCE_REPO_MISMATCH", json.dumps(candidate, indent=2))

    declared_gates = set(candidate.get("required_gates", []))
    missing_declared = sorted(set(REQUIRED_GATES).difference(declared_gates))
    if missing_declared:
        fail("RELEASE_DECLARED_GATE_MISSING", ",".join(missing_declared))

    readiness = parse_json(
        run([sys.executable, "-m", "verifrax.cli", "self", "release-readiness"]),
        "RELEASE_READINESS_CLI_NON_JSON_OUTPUT",
    )

    if readiness.get("status") != "PASS":
        fail("RELEASE_READINESS_REFUSED", json.dumps(readiness, indent=2))

    if os.environ.get("VERIFRAX_RELEASE_GATE_NO_NESTED") == "1":
        print(json.dumps({
            "status": "PASS",
            "gate": "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
            "package": "verifrax",
            "version": "0.1.0",
            "source_repo": "Verifrax/VERIFRAX-PY",
            "nested_gates_skipped": True,
            "required_gates_declared": candidate.get("required_gates", []),
        }, indent=2))
        return

    gate_outputs = [
        run([sys.executable, "scripts/check-api-machine-contract-replay-boundary.py"]),
        run([sys.executable, "scripts/check-receipt-verdict-projection-replay-boundary.py"]),
        run([sys.executable, "scripts/check-terminal-nonrecognition-nonrecourse-guard.py"]),
        run([sys.executable, "scripts/check-pytest-warning-free-release-gate.py"]),
    ]

    parsed = [parse_json(output, "GATE_NON_JSON_OUTPUT") for output in gate_outputs]
    failed = [item for item in parsed if item.get("status") != "PASS"]
    if failed:
        fail("RELEASE_REQUIRED_GATE_FAILED", json.dumps(failed, indent=2))

    passed = [item.get("gate") for item in parsed] + ["RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY"]

    print(json.dumps({
        "status": "PASS",
        "gate": "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "validated_gates_passed": passed,
        "required_gates_declared": candidate.get("required_gates", []),
        "release_target": {
            "tag": "v0.1.0",
            "pypi_project": "verifrax",
            "trusted_publishing_required": True,
            "attestation_required": True,
            "testpypi_rehearsal_required": True,
            "pytest_warning_free_required": True
        }
    }, indent=2))


if __name__ == "__main__":
    main()
