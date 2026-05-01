from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEAL = ROOT / "PYPI_TRUSTED_PUBLISHER_READINESS.json"


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "PYPI_TRUSTED_PUBLISHER_READINESS_SEAL",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def read(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        fail("REQUIRED_FILE_MISSING", path)
    return p.read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    p = ROOT / path
    if not p.exists():
        fail("REQUIRED_JSON_MISSING", path)
    return json.loads(p.read_text(encoding="utf-8"))


def run_json_gate(cmd: list[str], code: str) -> dict:
    output = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    ).stdout

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


def require_contains(name: str, text: str, needles: list[str]) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        fail("WORKFLOW_BINDING_MISSING", f"{name}: {missing}")


def main() -> None:
    if not SEAL.exists():
        fail("READINESS_SEAL_MISSING", str(SEAL))

    seal = json.loads(SEAL.read_text(encoding="utf-8"))

    if seal.get("do_not_publish") is not True:
        fail("DO_NOT_PUBLISH_FLAG_MISSING", json.dumps(seal, indent=2))

    if seal.get("production_publish_blocked_until_external_trusted_publishers_exist") is not True:
        fail("PRODUCTION_BLOCK_FLAG_MISSING", json.dumps(seal, indent=2))

    expected = {
        ("testpypi", "project_name"): "verifrax",
        ("testpypi", "owner"): "Verifrax",
        ("testpypi", "repository"): "VERIFRAX-PY",
        ("testpypi", "workflow_filename"): "testpypi-publish.yml",
        ("testpypi", "environment"): "testpypi",
        ("testpypi", "oidc_sub"): "repo:Verifrax/VERIFRAX-PY:environment:testpypi",
        ("pypi", "project_name"): "verifrax",
        ("pypi", "owner"): "Verifrax",
        ("pypi", "repository"): "VERIFRAX-PY",
        ("pypi", "workflow_filename"): "pypi-publish.yml",
        ("pypi", "environment"): "pypi",
        ("pypi", "oidc_sub"): "repo:Verifrax/VERIFRAX-PY:environment:pypi",
    }

    for (section, key), value in expected.items():
        if seal.get(section, {}).get(key) != value:
            fail("PUBLISHER_CLAIM_MISMATCH", f"{section}.{key}={seal.get(section, {}).get(key)!r}")

    testpypi_workflow = read(".github/workflows/testpypi-publish.yml")
    require_contains("testpypi-publish.yml", testpypi_workflow, [
        "on:\n  workflow_dispatch:",
        "id-token: write",
        "environment: testpypi",
        "repository-url: https://test.pypi.org/legacy/",
        "python scripts/check-pypi-trusted-publisher-readiness-seal.py",
        "python scripts/check-v010-release-admissibility-closure-boundary.py",
    ])

    pypi_workflow = read(".github/workflows/pypi-publish.yml")
    require_contains("pypi-publish.yml", pypi_workflow, [
        "on:\n  workflow_dispatch:",
        "id-token: write",
        "environment: pypi",
        "python scripts/check-pypi-trusted-publisher-readiness-seal.py",
        "python scripts/check-v010-release-admissibility-closure-boundary.py",
    ])

    custody = load_json("PYPI_CUSTODY.json")
    readiness = custody.get("trusted_publisher_readiness", {})
    if readiness.get("status") != "DECLARED_NOT_PUBLISHED":
        fail("CUSTODY_READINESS_STATUS_INVALID", json.dumps(readiness, indent=2))

    if readiness.get("do_not_publish") is not True:
        fail("CUSTODY_DO_NOT_PUBLISH_MISSING", json.dumps(readiness, indent=2))

    requirements = custody.get("release_requirements", {})
    for key in [
        "testpypi_pending_trusted_publisher_required",
        "pypi_pending_trusted_publisher_required",
        "do_not_publish_without_testpypi_live_rehearsal_proof",
    ]:
        if requirements.get(key) is not True:
            fail("CUSTODY_REQUIREMENT_MISSING", key)

    closure = run_json_gate(
        [sys.executable, "scripts/check-v010-release-admissibility-closure-boundary.py"],
        "V010_CLOSURE_NON_JSON_OUTPUT",
    )

    if closure.get("status") != "PASS":
        fail("V010_CLOSURE_NOT_PASSING", json.dumps(closure, indent=2))

    print(json.dumps({
        "status": "PASS",
        "gate": "PYPI_TRUSTED_PUBLISHER_READINESS_SEAL",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "do_not_publish": True,
        "testpypi_pending_trusted_publisher": {
            "owner": "Verifrax",
            "repository": "VERIFRAX-PY",
            "workflow": "testpypi-publish.yml",
            "environment": "testpypi"
        },
        "pypi_pending_trusted_publisher": {
            "owner": "Verifrax",
            "repository": "VERIFRAX-PY",
            "workflow": "pypi-publish.yml",
            "environment": "pypi"
        },
        "repo_side_ready": True,
        "external_publishers_still_manual": True
    }, indent=2))


if __name__ == "__main__":
    main()
