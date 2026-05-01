from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY",
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


def require(path: str) -> None:
    if not (ROOT / path).exists():
        fail("TESTPYPI_REQUIRED_FILE_MISSING", path)


def main() -> None:
    required = [
        "TESTPYPI_REHEARSAL.json",
        "RELEASE_CANDIDATE.json",
        "PYPI_CUSTODY.json",
        ".github/workflows/testpypi-publish.yml",
        "scripts/check-release-candidate-attestation-readiness-boundary.py",
        "scripts/check-pypi-custody-attestation-release-gate.py",
        "scripts/check-distribution-installation-replay-proof.py"
    ]

    for path in required:
        require(path)

    workflow = (ROOT / ".github/workflows/testpypi-publish.yml").read_text(encoding="utf-8")
    for needle in [
        "name: testpypi-publish",
        "id-token: write",
        "environment: testpypi",
        "repository-url: https://test.pypi.org/legacy/"
    ]:
        if needle not in workflow:
            fail("TESTPYPI_WORKFLOW_BINDING_MISSING", needle)

    manifest = json.loads((ROOT / "TESTPYPI_REHEARSAL.json").read_text(encoding="utf-8"))
    if manifest.get("publisher", {}).get("method") != "pypi-trusted-publishing":
        fail("TESTPYPI_TRUSTED_PUBLISHING_NOT_BOUND", json.dumps(manifest, indent=2))

    readiness = parse_json(
        run([sys.executable, "-m", "verifrax.cli", "self", "testpypi-readiness"]),
        "TESTPYPI_READINESS_CLI_NON_JSON_OUTPUT",
    )

    if readiness.get("status") != "PASS":
        fail("TESTPYPI_READINESS_REFUSED", json.dumps(readiness, indent=2))

    release_candidate = parse_json(
        run([sys.executable, "scripts/check-release-candidate-attestation-readiness-boundary.py"]),
        "RELEASE_CANDIDATE_GATE_NON_JSON_OUTPUT",
    )

    if release_candidate.get("status") != "PASS":
        fail("RELEASE_CANDIDATE_GATE_FAILED", json.dumps(release_candidate, indent=2))

    distribution = parse_json(
        run([sys.executable, "scripts/check-distribution-installation-replay-proof.py"]),
        "DISTRIBUTION_REPLAY_GATE_NON_JSON_OUTPUT",
    )

    if distribution.get("status") != "PASS":
        fail("DISTRIBUTION_REPLAY_GATE_FAILED", json.dumps(distribution, indent=2))

    print(json.dumps({
        "status": "PASS",
        "gate": "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "testpypi_project": "verifrax",
        "trusted_publishing_required": True,
        "attestation_required": True,
        "production_publish_blocked_without_rehearsal": True
    }, indent=2))


if __name__ == "__main__":
    main()
