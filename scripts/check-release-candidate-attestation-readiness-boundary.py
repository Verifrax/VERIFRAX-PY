from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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

        trailing = stripped[idx + end:].strip()
        if trailing == "":
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
        ".github/workflows/test.yml",
        ".github/workflows/api-machine-contract-replay-boundary.yml",
        ".github/workflows/receipt-verdict-projection-replay-boundary.yml",
        ".github/workflows/terminal-nonrecognition-nonrecourse-guard.yml",
        ".github/workflows/pypi-release-gate.yml",
        ".github/workflows/distribution-installation-replay-proof.yml",
        ".github/workflows/pypi-publish.yml",
        "scripts/check-api-machine-contract-replay-boundary.py",
        "scripts/check-receipt-verdict-projection-replay-boundary.py",
        "scripts/check-terminal-nonrecognition-nonrecourse-guard.py",
        "scripts/check-pypi-custody-attestation-release-gate.py",
        "scripts/check-distribution-installation-replay-proof.py",
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

    readiness = parse_json(
        run([sys.executable, "-m", "verifrax.cli", "self", "release-readiness"]),
        "RELEASE_READINESS_CLI_NON_JSON_OUTPUT",
    )

    if readiness.get("status") != "PASS":
        fail("RELEASE_READINESS_REFUSED", json.dumps(readiness, indent=2))

    gate_outputs = [
        run([sys.executable, "scripts/check-api-machine-contract-replay-boundary.py"]),
        run([sys.executable, "scripts/check-receipt-verdict-projection-replay-boundary.py"]),
        run([sys.executable, "scripts/check-terminal-nonrecognition-nonrecourse-guard.py"]),
        run([sys.executable, "scripts/check-pypi-custody-attestation-release-gate.py"]),
        run([sys.executable, "scripts/check-distribution-installation-replay-proof.py"]),
    ]

    parsed = [parse_json(output, "GATE_NON_JSON_OUTPUT") for output in gate_outputs]
    failed = [item for item in parsed if item.get("status") != "PASS"]
    if failed:
        fail("RELEASE_REQUIRED_GATE_FAILED", json.dumps(failed, indent=2))

    print(json.dumps({
        "status": "PASS",
        "gate": "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "required_gates_passed": [item.get("gate") for item in parsed],
        "release_target": {
            "tag": "v0.1.0",
            "pypi_project": "verifrax",
            "trusted_publishing_required": True,
            "attestation_required": True
        }
    }, indent=2))


if __name__ == "__main__":
    main()
