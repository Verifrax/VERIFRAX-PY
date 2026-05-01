from pathlib import Path


def test_distribution_replay_script_exists():
    script = Path("scripts/check-distribution-installation-replay-proof.py")
    assert script.exists()
    text = script.read_text()
    assert "DISTRIBUTION_INSTALLATION_REPLAY_PROOF" in text
    assert "OBJECT_CHAIN_INCOMPLETE" in text
    assert "Verifrax/VERIFRAX-PY" in text


def test_distribution_replay_workflow_exists():
    workflow = Path(".github/workflows/distribution-installation-replay-proof.yml")
    assert workflow.exists()
    text = workflow.read_text()
    assert "check-distribution-installation-replay-proof.py" in text
    assert "python-version: \"3.12\"" in text
