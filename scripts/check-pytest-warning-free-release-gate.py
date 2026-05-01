from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "PYTEST_WARNING_FREE_RELEASE_GATE",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def main() -> None:
    completed = subprocess.run(
        [sys.executable, "-W", "error", "-m", "pytest"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if completed.returncode != 0:
        fail("PYTEST_WARNING_OR_FAILURE_PRESENT", completed.stdout)

    print(json.dumps({
        "status": "PASS",
        "gate": "PYTEST_WARNING_FREE_RELEASE_GATE",
        "package": "verifrax",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "warnings_as_errors": True,
        "pytest_returncode": completed.returncode
    }, indent=2))


if __name__ == "__main__":
    main()
