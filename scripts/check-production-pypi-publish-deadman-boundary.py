from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_POLICY.json"
WORKFLOW = ROOT / ".github/workflows/pypi-publish.yml"
AUTH_CHECK = "python scripts/check-production-pypi-publish-authorization-boundary.py"


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "PRODUCTION_PYPI_PUBLISH_DEADMAN_BOUNDARY",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def parse_json(output: str) -> dict:
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
    fail("AUTHORIZATION_OUTPUT_NON_JSON", output)


def main() -> None:
    if not POLICY.exists():
        fail("PRODUCTION_PYPI_AUTHORIZATION_POLICY_MISSING", str(POLICY.relative_to(ROOT)))

    if not WORKFLOW.exists():
        fail("PYPI_PUBLISH_WORKFLOW_MISSING", str(WORKFLOW.relative_to(ROOT)))

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    workflow = WORKFLOW.read_text(encoding="utf-8")

    if policy.get("do_not_publish") is not True:
        fail("DEADMAN_POLICY_DO_NOT_PUBLISH_MISSING", json.dumps(policy, indent=2))

    required_workflow_needles = [
        "on:\n  workflow_dispatch:",
        "id-token: write",
        "environment: pypi",
        AUTH_CHECK,
        "python scripts/check-pypi-trusted-publisher-readiness-seal.py",
        "python scripts/check-v010-release-admissibility-closure-boundary.py",
        "uses: pypa/gh-action-pypi-publish@release/v1",
    ]

    missing = [needle for needle in required_workflow_needles if needle not in workflow]
    if missing:
        fail("PYPI_PUBLISH_WORKFLOW_DEADMAN_BINDING_MISSING", json.dumps(missing, indent=2))

    auth_index = workflow.index(AUTH_CHECK)
    build_index = workflow.index("python -m build")
    publish_index = workflow.index("uses: pypa/gh-action-pypi-publish@release/v1")

    if not auth_index < build_index < publish_index:
        fail("PYPI_PUBLISH_WORKFLOW_DEADMAN_ORDER_INVALID", "authorization check must run before build and publish")

    completed = subprocess.run(
        [sys.executable, "scripts/check-production-pypi-publish-authorization-boundary.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if completed.returncode == 0:
        fail("PRODUCTION_AUTHORIZATION_UNEXPECTEDLY_OPEN", completed.stdout)

    parsed = parse_json(completed.stdout)

    if parsed.get("gate") != "PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_BOUNDARY":
        fail("AUTHORIZATION_GATE_MISMATCH", json.dumps(parsed, indent=2))

    if parsed.get("code") not in {
        "PRODUCTION_PYPI_AUTHORIZATION_MISSING",
        "PRODUCTION_PYPI_PUBLISH_NOT_ALLOWED",
        "PRODUCTION_PYPI_DO_NOT_PUBLISH_ACTIVE",
        "TESTPYPI_LIVE_REHEARSAL_PROOF_MISSING",
        "TESTPYPI_LIVE_REHEARSAL_PROOF_INVALID",
        "PRODUCTION_PYPI_AUTHORIZATION_MISMATCH",
    }:
        fail("UNEXPECTED_AUTHORIZATION_REFUSAL", json.dumps(parsed, indent=2))

    print(json.dumps({
        "status": "PASS",
        "gate": "PRODUCTION_PYPI_PUBLISH_DEADMAN_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "publish_workflow_manual_only": True,
        "authorization_check_before_build": True,
        "authorization_check_before_publish": True,
        "current_publish_state": "REFUSED_BY_DESIGN",
        "current_refusal": parsed.get("code"),
        "no_publish_executed": True
    }, indent=2))


if __name__ == "__main__":
    main()
