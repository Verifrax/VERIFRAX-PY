from pathlib import Path


def test_projection_replay_gate_exists():
    script = Path("scripts/check-receipt-verdict-projection-replay-boundary.py")
    assert script.exists()
    text = script.read_text()
    assert "RECEIPT_VERDICT_PROJECTION_REPLAY_BOUNDARY" in text
    assert "Verifrax/CORPIFORM" in text
    assert "Verifrax/VERIFRAX" in text
    assert "Verifrax/VERIFRAX-PY" in text


def test_projection_replay_workflow_exists():
    workflow = Path(".github/workflows/receipt-verdict-projection-replay-boundary.yml")
    assert workflow.exists()
    text = workflow.read_text()
    assert "check-receipt-verdict-projection-replay-boundary.py" in text
    assert "python-version: \"3.12\"" in text
