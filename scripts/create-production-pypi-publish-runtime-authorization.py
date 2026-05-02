from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "evidence/testpypi-live-rehearsal/TESTPYPI_LIVE_REHEARSAL_PROOF.json"
AUTH = ROOT / "PYPI_PRODUCTION_PUBLISH_AUTHORIZATION.json"

def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "PRODUCTION_PYPI_RUNTIME_AUTHORIZATION_CREATION_BOUNDARY",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)

if AUTH.exists():
    fail("PRODUCTION_AUTHORIZATION_FILE_MUST_NOT_BE_COMMITTED", str(AUTH.relative_to(ROOT)))

if not PROOF.exists():
    fail("TESTPYPI_LIVE_REHEARSAL_PROOF_MISSING", str(PROOF.relative_to(ROOT)))

proof = json.loads(PROOF.read_text(encoding="utf-8"))

expected = {
    "status": "PASS",
    "index": "testpypi",
    "package": "verifrax",
    "testpypi_project": "verifrax",
    "version": "0.1.0",
    "source_repo": "Verifrax/VERIFRAX-PY",
    "installed_from_testpypi": True,
    "trusted_publishing_rehearsal": True,
    "import_verified": True,
    "production_publish_admissibility_input": True,
    "production_publish_admissible_after_testpypi_rehearsal": True,
    "workflow": "testpypi-publish.yml",
    "workflow_conclusion": "success",
}

for key, value in expected.items():
    if proof.get(key) != value:
        fail("TESTPYPI_LIVE_REHEARSAL_PROOF_INVALID", f"{key}={proof.get(key)!r}")

if not str(proof.get("workflow_run_url", "")).startswith(
    "https://github.com/Verifrax/VERIFRAX-PY/actions/runs/"
):
    fail("TESTPYPI_LIVE_REHEARSAL_PROOF_INVALID", "workflow_run_url")

authorization = {
    "schema": "verifrax.python.production-pypi-publish-authorization.v1",
    "status": "PASS",
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

AUTH.write_text(json.dumps(authorization, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "status": "PASS",
    "gate": "PRODUCTION_PYPI_RUNTIME_AUTHORIZATION_CREATION_BOUNDARY",
    "package": "verifrax",
    "version": "0.1.0",
    "authorization_file_created_runtime_only": str(AUTH.relative_to(ROOT)),
    "committed_authorization_file_required": False,
}, indent=2))
