from pathlib import Path


def test_terminal_boundary_manifest_exists():
    data = Path("TERMINAL_BOUNDARY.json").read_text()
    assert "VERIFICATION_IS_NOT_TERMINAL_RECOGNITION_OR_TERMINAL_RECOURSE" in data
    assert "Verifrax/ANAGNORIUM" in data
    assert "Verifrax/REGRESSORIUM" in data


def test_terminal_guard_script_exists():
    script = Path("scripts/check-terminal-nonrecognition-nonrecourse-guard.py")
    assert script.exists()
    text = script.read_text()
    assert "TERMINAL_NONRECOGNITION_NONRECOURSE_GUARD" in text
    assert "VERIFICATION_DOES_NOT_IMPLY_TERMINAL_RECOGNITION_OR_TERMINAL_RECOURSE" in text


def test_terminal_guard_workflow_exists():
    workflow = Path(".github/workflows/terminal-nonrecognition-nonrecourse-guard.yml")
    assert workflow.exists()
    text = workflow.read_text()
    assert "check-terminal-nonrecognition-nonrecourse-guard.py" in text
    assert "python-version: \"3.12\"" in text
