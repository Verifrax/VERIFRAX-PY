import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_cold_clone_no_publish_replay_boundary_static_contract():
    ledger = json.loads((ROOT / "COLD_CLONE_NO_PUBLISH_REPLAY.json").read_text())
    workflow = (ROOT / ".github/workflows/cold-clone-no-publish-replay-boundary.yml").read_text()
    check = (ROOT / "scripts/check-cold-clone-no-publish-replay-boundary.py").read_text()

    assert ledger["do_not_publish"] is True
    assert ledger["publish_default"] == "REFUSE"
    assert ledger["isolated_venv"] is True
    assert "scripts/check-publish-workflow-order-lock-boundary.py" in ledger["required_gates"]
    assert "scripts/check-no-publish-final-readiness-ledger.py" in ledger["required_gates"]
    assert "check-cold-clone-no-publish-replay-boundary.py" in workflow
    assert "pypa/gh-action-pypi-publish" not in workflow
    assert "twine upload" not in check
    assert "gh release upload" not in check
