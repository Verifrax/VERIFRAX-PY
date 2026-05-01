from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RECEIPT = ROOT / "examples/receipt-projection-fixture.json"
VERDICT = ROOT / "examples/verdict-projection-fixture.json"
INCOMPLETE_RECEIPT = ROOT / "examples/incomplete-receipt-projection.json"


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "RECEIPT_VERDICT_PROJECTION_REPLAY_BOUNDARY",
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


def parse_cli_json(output: str, code: str) -> dict:
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        fail(code, output)


def main() -> None:
    for required in [RECEIPT, VERDICT, INCOMPLETE_RECEIPT]:
        if not required.exists():
            fail("PROJECTION_FIXTURE_MISSING", str(required))

    receipt = parse_cli_json(
        run([sys.executable, "-m", "verifrax.cli", "receipt", "inspect", str(RECEIPT)]),
        "RECEIPT_CLI_NON_JSON_OUTPUT",
    )

    if receipt.get("status") != "PASS":
        fail("RECEIPT_PROJECTION_REFUSED", json.dumps(receipt, indent=2))

    if receipt.get("source_repo") != "Verifrax/CORPIFORM":
        fail("RECEIPT_SOURCE_REPO_MISMATCH", json.dumps(receipt, indent=2))

    if receipt.get("package_boundary") != "Verifrax/VERIFRAX-PY":
        fail("RECEIPT_PACKAGE_BOUNDARY_MISMATCH", json.dumps(receipt, indent=2))

    verdict = parse_cli_json(
        run([sys.executable, "-m", "verifrax.cli", "verdict", "inspect", str(VERDICT)]),
        "VERDICT_CLI_NON_JSON_OUTPUT",
    )

    if verdict.get("status") != "PASS":
        fail("VERDICT_PROJECTION_REFUSED", json.dumps(verdict, indent=2))

    if verdict.get("source_repo") != "Verifrax/VERIFRAX":
        fail("VERDICT_SOURCE_REPO_MISMATCH", json.dumps(verdict, indent=2))

    if verdict.get("package_boundary") != "Verifrax/VERIFRAX-PY":
        fail("VERDICT_PACKAGE_BOUNDARY_MISMATCH", json.dumps(verdict, indent=2))

    incomplete = parse_cli_json(
        run([sys.executable, "-m", "verifrax.cli", "receipt", "inspect", str(INCOMPLETE_RECEIPT)]),
        "INCOMPLETE_RECEIPT_CLI_NON_JSON_OUTPUT",
    )

    if incomplete.get("status") != "REFUSED":
        fail("INCOMPLETE_RECEIPT_NOT_REFUSED", json.dumps(incomplete, indent=2))

    if "RECEIPT_PROJECTION_INCOMPLETE" not in incomplete.get("blocking_refusals", []):
        fail("INCOMPLETE_RECEIPT_REFUSAL_MISSING", json.dumps(incomplete, indent=2))

    print(json.dumps({
        "status": "PASS",
        "gate": "RECEIPT_VERDICT_PROJECTION_REPLAY_BOUNDARY",
        "receipt_source_repo": "Verifrax/CORPIFORM",
        "verdict_source_repo": "Verifrax/VERIFRAX",
        "api_boundary": "Verifrax/VERIFRAX-API",
        "package_boundary": "Verifrax/VERIFRAX-PY",
        "incomplete_projection_refusal": "RECEIPT_PROJECTION_INCOMPLETE"
    }, indent=2))


if __name__ == "__main__":
    main()
