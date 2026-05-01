from pathlib import Path


def test_pytest_warning_free_release_gate_exists():
    script = Path("scripts/check-pytest-warning-free-release-gate.py")
    assert script.exists()
    text = script.read_text()
    assert "PYTEST_WARNING_FREE_RELEASE_GATE" in text
    assert "-W" in text
    assert "error" in text
    assert "PYTEST_WARNING_TEXT_PRESENT" not in text
    assert "warnings_as_errors" in text
