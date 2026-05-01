from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SAFE_VERDICT = ROOT / "examples/terminal-safe-verdict-fixture.json"
OVERCLAIM_VERDICT = ROOT / "examples/terminal-overclaim-verdict-fixture.json"
RECOGNITION = ROOT / "examples/terminal-recognition-fixture.json"
RECOURSE_WITHOUT_RECOGNITION = ROOT / "examples/terminal-recourse-without-recognition-fixture.json"


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "TERMINAL_NONRECOGNITION_NONRECOURSE_GUARD",
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


def parse(output: str, code: str) -> dict:
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        fail(code, output)


def inspect(path: Path) -> dict:
    return parse(
        run([sys.executable, "-m", "verifrax.cli", "terminal", "inspect", str(path)]),
        f"NON_JSON_OUTPUT:{path.name}",
    )


def main() -> None:
    for path in [SAFE_VERDICT, OVERCLAIM_VERDICT, RECOGNITION, RECOURSE_WITHOUT_RECOGNITION]:
        if not path.exists():
            fail("TERMINAL_FIXTURE_MISSING", str(path))

    safe = inspect(SAFE_VERDICT)
    if safe.get("status") != "PASS":
        fail("SAFE_VERDICT_NOT_ACCEPTED", json.dumps(safe, indent=2))
    if safe.get("recognition_terminal") is not False:
        fail("SAFE_VERDICT_RECOGNITION_OVERCLAIM", json.dumps(safe, indent=2))
    if safe.get("recourse_terminal") is not False:
        fail("SAFE_VERDICT_RECOURSE_OVERCLAIM", json.dumps(safe, indent=2))
    for warning in ["VERIFICATION_IS_NOT_RECOGNITION", "VERIFICATION_IS_NOT_RECOURSE"]:
        if warning not in safe.get("non_terminal_warnings", []):
            fail("SAFE_VERDICT_WARNING_MISSING", warning)

    overclaim = inspect(OVERCLAIM_VERDICT)
    if overclaim.get("status") != "REFUSED":
        fail("OVERCLAIM_VERDICT_NOT_REFUSED", json.dumps(overclaim, indent=2))
    for refusal in [
        "TERMINAL_RECOGNITION_OVERCLAIM",
        "TERMINAL_RECOURSE_OVERCLAIM",
        "RECOURSE_WITHOUT_RECOGNITION",
    ]:
        if refusal not in overclaim.get("blocking_refusals", []):
            fail("OVERCLAIM_REFUSAL_MISSING", refusal)

    recognition = inspect(RECOGNITION)
    if recognition.get("status") != "PASS":
        fail("RECOGNITION_FIXTURE_NOT_ACCEPTED", json.dumps(recognition, indent=2))
    if recognition.get("source_repo") != "Verifrax/ANAGNORIUM":
        fail("RECOGNITION_SOURCE_MISMATCH", json.dumps(recognition, indent=2))
    if recognition.get("recourse_terminal") is not False:
        fail("RECOGNITION_COLLAPSED_INTO_RECOURSE", json.dumps(recognition, indent=2))

    bad_recourse = inspect(RECOURSE_WITHOUT_RECOGNITION)
    if bad_recourse.get("status") != "REFUSED":
        fail("RECOURSE_WITHOUT_RECOGNITION_NOT_REFUSED", json.dumps(bad_recourse, indent=2))
    if "RECOURSE_WITHOUT_RECOGNITION" not in bad_recourse.get("blocking_refusals", []):
        fail("RECOURSE_WITHOUT_RECOGNITION_REFUSAL_MISSING", json.dumps(bad_recourse, indent=2))

    print(json.dumps({
        "status": "PASS",
        "gate": "TERMINAL_NONRECOGNITION_NONRECOURSE_GUARD",
        "package_boundary": "Verifrax/VERIFRAX-PY",
        "verification_source": "Verifrax/VERIFRAX",
        "recognition_source": "Verifrax/ANAGNORIUM",
        "recourse_source": "Verifrax/REGRESSORIUM",
        "guard": "VERIFICATION_DOES_NOT_IMPLY_TERMINAL_RECOGNITION_OR_TERMINAL_RECOURSE"
    }, indent=2))


if __name__ == "__main__":
    main()
