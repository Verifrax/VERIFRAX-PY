from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/api-contract-fixture.json"


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "API_MACHINE_CONTRACT_REPLAY_BOUNDARY",
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


def main() -> None:
    if not FIXTURE.exists():
        fail("API_CONTRACT_FIXTURE_MISSING", str(FIXTURE))

    contract = json.loads(FIXTURE.read_text(encoding="utf-8"))
    paths = contract.get("paths", {})
    required = [
        "/healthz",
        "/readyz",
        "/version",
        "/openapi.json",
        "/api/receipt/{id}",
        "/api/verdict/{id}",
    ]

    missing = [path for path in required if path not in paths]
    if missing:
        fail("API_CONTRACT_REQUIRED_PATH_MISSING", ",".join(missing))

    output = run([sys.executable, "-m", "verifrax.cli", "api-contract", "inspect", str(FIXTURE)])
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        fail("API_CONTRACT_CLI_NON_JSON_OUTPUT", output)

    if result.get("status") != "PASS":
        fail("API_CONTRACT_INSPECTION_REFUSED", output)

    if result.get("source_repo") != "Verifrax/VERIFRAX-API":
        fail("API_CONTRACT_SOURCE_REPO_MISMATCH", output)

    if result.get("package_repo") != "Verifrax/VERIFRAX-PY":
        fail("API_CONTRACT_PACKAGE_REPO_MISMATCH", output)

    print(json.dumps({
        "status": "PASS",
        "gate": "API_MACHINE_CONTRACT_REPLAY_BOUNDARY",
        "source_repo": "Verifrax/VERIFRAX-API",
        "package_repo": "Verifrax/VERIFRAX-PY",
        "required_paths": required,
    }, indent=2))


if __name__ == "__main__":
    main()
