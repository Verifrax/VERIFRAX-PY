from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_POLICY.json"
AUTHORIZATION = ROOT / "PYPI_PRODUCTION_PUBLISH_AUTHORIZATION.json"


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_BOUNDARY",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def load(path: Path, code: str) -> dict:
    if not path.exists():
        fail(code, str(path.relative_to(ROOT)))
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    policy = load(POLICY, "PRODUCTION_PYPI_AUTHORIZATION_POLICY_MISSING")

    if policy.get("do_not_publish") is not True:
        fail("PRODUCTION_PYPI_POLICY_DO_NOT_PUBLISH_MISSING", json.dumps(policy, indent=2))

    if not AUTHORIZATION.exists():
        fail("PRODUCTION_PYPI_AUTHORIZATION_MISSING", str(AUTHORIZATION.relative_to(ROOT)))

    authorization = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))

    expected = {
        "publish_allowed": True,
        "do_not_publish": False,
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "target": "pypi",
        "workflow": "pypi-publish.yml",
        "environment": "pypi",
        "testpypi_live_rehearsal_proof_required": True,
        "testpypi_live_rehearsal_proof_path": "evidence/testpypi-live-rehearsal/TESTPYPI_LIVE_REHEARSAL_PROOF.json",
    }

    for key, value in expected.items():
        if authorization.get(key) != value:
            fail("PRODUCTION_PYPI_AUTHORIZATION_MISMATCH", f"{key}={authorization.get(key)!r}")

    proof_path = ROOT / authorization["testpypi_live_rehearsal_proof_path"]
    proof = load(proof_path, "TESTPYPI_LIVE_REHEARSAL_PROOF_MISSING")

    proof_expected = {
        "status": "PASS",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "testpypi_project": "verifrax",
        "trusted_publishing_rehearsal": True,
        "installed_from_testpypi": True,
        "production_publish_admissibility_input": True,
    }

    for key, value in proof_expected.items():
        if proof.get(key) != value:
            fail("TESTPYPI_LIVE_REHEARSAL_PROOF_INVALID", f"{key}={proof.get(key)!r}")

    if not str(proof.get("workflow_run_url", "")).startswith("https://github.com/Verifrax/VERIFRAX-PY/actions/runs/"):
        fail("TESTPYPI_LIVE_REHEARSAL_PROOF_INVALID", "workflow_run_url")

    print(json.dumps({
        "status": "PASS",
        "gate": "PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_BOUNDARY",
        "package": "verifrax",
        "version": "0.1.0",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "target": "pypi",
        "publish_allowed": True,
        "testpypi_live_rehearsal_proof": str(proof_path.relative_to(ROOT))
    }, indent=2))


if __name__ == "__main__":
    main()
