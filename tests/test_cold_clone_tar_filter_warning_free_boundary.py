import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_cold_clone_tar_filter_warning_free_static_contract():
    ledger = json.loads((ROOT / "COLD_CLONE_TAR_FILTER_WARNING_FREE.json").read_text())
    cold = (ROOT / "scripts/check-cold-clone-no-publish-replay-boundary.py").read_text()
    check = (ROOT / "scripts/check-cold-clone-tar-filter-warning-free-boundary.py").read_text()
    workflow = (ROOT / ".github/workflows/cold-clone-tar-filter-warning-free-boundary.yml").read_text()

    assert ledger["do_not_publish"] is True
    assert ledger["publish_default"] == "REFUSE"
    assert ledger["tar_extract_filter"] == "data"
    assert ledger["python_314_deprecation_warning_refusal"] is True
    assert 'tf.extractall(work, filter="data")' in cold
    assert "tf.extractall(work)" not in cold
    assert "DeprecationWarning" in check
    assert "check-cold-clone-tar-filter-warning-free-boundary.py" in workflow
    assert "pypa/gh-action-pypi-publish" not in workflow
    assert "twine upload" not in check
