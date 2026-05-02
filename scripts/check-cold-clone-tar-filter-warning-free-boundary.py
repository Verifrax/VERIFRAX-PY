from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / "COLD_CLONE_TAR_FILTER_WARNING_FREE.json").read_text())

cold_check = (ROOT / "scripts/check-cold-clone-no-publish-replay-boundary.py").read_text()

assert LEDGER["schema"] == "verifrax.python.cold-clone-tar-filter-warning-free.v1"
assert LEDGER["package"] == "verifrax"
assert LEDGER["version"] == "0.1.0"
assert LEDGER["source_repo"] == "Verifrax/VERIFRAX-PY"
assert LEDGER["do_not_publish"] is True
assert LEDGER["publish_default"] == "REFUSE"
assert LEDGER["tar_extract_filter"] == "data"
assert LEDGER["python_314_deprecation_warning_refusal"] is True
assert LEDGER["cold_clone_replay_warning_free_required"] is True
assert LEDGER["no_publish_executed"] is True

assert 'tf.extractall(work, filter="data")' in cold_check
assert "tf.extractall(work)" not in cold_check
assert ("twine" + " upload") not in cold_check
assert ("gh release" + " upload") not in cold_check
assert ("pypa/gh-action-" + "pypi-publish") not in cold_check

proc = subprocess.run(
    [sys.executable, "scripts/check-cold-clone-no-publish-replay-boundary.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)

combined = proc.stdout + proc.stderr
if proc.returncode != 0:
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    raise SystemExit(proc.returncode)

if "DeprecationWarning" in combined:
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    raise AssertionError("COLD_CLONE_REPLAY_EMITTED_DEPRECATION_WARNING")

print(json.dumps({
    "status": "PASS",
    "gate": "COLD_CLONE_TAR_FILTER_WARNING_FREE_BOUNDARY",
    "package": LEDGER["package"],
    "version": LEDGER["version"],
    "source_repo": LEDGER["source_repo"],
    "tar_extract_filter": LEDGER["tar_extract_filter"],
    "python_314_deprecation_warning_refusal": True,
    "cold_clone_replay_warning_free": True,
    "do_not_publish": True,
    "publish_default": "REFUSE",
    "no_publish_executed": True
}, indent=2))
