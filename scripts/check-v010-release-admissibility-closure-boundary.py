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
        "gate": "V010_RELEASE_ADMISSIBILITY_CLOSURE_BOUNDARY",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def run(cmd: list[str], extra_env: dict[str, str] | None = None) -> str:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
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


def main() -> None:
    candidate = json.loads((ROOT / "RELEASE_CANDIDATE.json").read_text(encoding="utf-8"))
    custody = json.loads((ROOT / "PYPI_CUSTODY.json").read_text(encoding="utf-8"))

    candidate_gates = set(candidate.get("required_gates", []))
    missing = sorted(set(REQUIRED_GATES).difference(candidate_gates))
    if missing:
        fail("V010_RELEASE_REQUIRED_GATE_MISSING", ",".join(missing))

    requirements = custody.get("release_requirements", {})
    required_flags = {
        "trusted_publishing_required",
        "attestation_required",
        "sdist_required",
        "wheel_required",
        "testpypi_rehearsal_required",
        "release_candidate_readiness_required",
        "pytest_warning_free_required",
        "terminal_nonrecognition_nonrecourse_guard_required",
        "receipt_verdict_projection_replay_required",
        "api_machine_contract_replay_required",
    }

    missing_flags = sorted(flag for flag in required_flags if requirements.get(flag) is not True)
    if missing_flags:
        fail("V010_CUSTODY_REQUIRED_FLAG_MISSING", ",".join(missing_flags))

    nested_off = {"VERIFRAX_RELEASE_GATE_NO_NESTED": "1"}

    outputs = [
        run([sys.executable, "scripts/check-api-machine-contract-replay-boundary.py"]),
        run([sys.executable, "scripts/check-receipt-verdict-projection-replay-boundary.py"]),
        run([sys.executable, "scripts/check-terminal-nonrecognition-nonrecourse-guard.py"]),
        run([sys.executable, "scripts/check-pypi-custody-attestation-release-gate.py"]),
        run([sys.executable, "scripts/check-distribution-installation-replay-proof.py"]),
        run([sys.executable, "scripts/check-pytest-warning-free-release-gate.py"]),
        run([sys.executable, "scripts/check-release-candidate-attestation-readiness-boundary.py"], nested_off),
        run([sys.executable, "scripts/check-testpypi-rehearsal-attestation-boundary.py"], nested_off),
    ]

    parsed = [parse_json(output, "V010_GATE_NON_JSON_OUTPUT") for output in outputs]
    failed = [item for item in parsed if item.get("status") != "PASS"]
    if failed:
        fail("V010_RELEASE_GATE_FAILED", json.dumps(failed, indent=2))

    passed = [item.get("gate") for item in parsed]
    missing_runtime = sorted(set(REQUIRED_GATES).difference(passed))
    if missing_runtime:
        fail("V010_RUNTIME_GATE_MISSING", ",".join(missing_runtime))

    print(json.dumps({
        "status": "PASS",
        "gate": "V010_RELEASE_ADMISSIBILITY_CLOSURE_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "required_gates_passed": passed,
        "production_publish_admissible_after_testpypi_rehearsal": True
    }, indent=2))


if __name__ == "__main__":
    main()
