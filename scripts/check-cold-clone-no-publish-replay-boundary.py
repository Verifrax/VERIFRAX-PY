from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / "COLD_CLONE_NO_PUBLISH_REPLAY.json").read_text())

REQUIRED_GATES = LEDGER["required_gates"]

def run(cmd: list[str], cwd: Path, *, stdout=None) -> None:
    subprocess.check_call(cmd, cwd=cwd, stdout=stdout)

assert LEDGER["schema"] == "verifrax.python.cold-clone-no-publish-replay.v1"
assert LEDGER["package"] == "verifrax"
assert LEDGER["version"] == "0.1.0"
assert LEDGER["source_repo"] == "Verifrax/VERIFRAX-PY"
assert LEDGER["do_not_publish"] is True
assert LEDGER["publish_default"] == "REFUSE"
assert LEDGER["isolated_venv"] is True
assert LEDGER["no_publish_executed"] is True
assert "scripts/check-publish-workflow-order-lock-boundary.py" in REQUIRED_GATES
assert "scripts/check-no-publish-final-readiness-ledger.py" in REQUIRED_GATES

with tempfile.TemporaryDirectory(prefix="verifrax-py-cold-replay-") as td:
    td_path = Path(td)
    archive = td_path / "tree.tar"
    work = td_path / "repo"
    work.mkdir()

    tree = subprocess.check_output(["git", "write-tree"], cwd=ROOT, text=True).strip()

    with archive.open("wb") as fh:
        run(["git", "archive", "--format=tar", tree], cwd=ROOT, stdout=fh)

    with tarfile.open(archive) as tf:
        tf.extractall(work, filter="data")

    py = sys.executable
    run([py, "-m", "compileall", "-q", "src", "tests", "scripts"], cwd=work)
    run([py, "-m", "venv", ".venv"], cwd=work)

    venv_python = work / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=work, stdout=subprocess.DEVNULL)
    run([str(venv_python), "-m", "pip", "install", "-e", ".[test,build]"], cwd=work, stdout=subprocess.DEVNULL)

    run([str(venv_python), "-m", "pytest", "-q"], cwd=work)

    for gate in REQUIRED_GATES:
        run([str(venv_python), gate], cwd=work)

print(json.dumps({
    "status": "PASS",
    "gate": "COLD_CLONE_NO_PUBLISH_REPLAY_BOUNDARY",
    "package": LEDGER["package"],
    "version": LEDGER["version"],
    "source_repo": LEDGER["source_repo"],
    "replay_mode": LEDGER["replay_mode"],
    "isolated_venv": True,
    "required_gates_passed": REQUIRED_GATES,
    "do_not_publish": True,
    "publish_default": "REFUSE",
    "no_publish_executed": True
}, indent=2))
