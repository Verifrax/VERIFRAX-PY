import json
from pathlib import Path

from verifrax.terminal import inspect_terminal_boundary


def load(path: str) -> dict:
    return json.loads(Path(path).read_text())


def test_safe_verdict_is_not_terminal_recognition_or_recourse():
    result = inspect_terminal_boundary(load("examples/terminal-safe-verdict-fixture.json"))
    assert result["status"] == "PASS"
    assert result["accepted"] is True
    assert result["recognition_terminal"] is False
    assert result["recourse_terminal"] is False
    assert "VERIFICATION_IS_NOT_RECOGNITION" in result["non_terminal_warnings"]
    assert "VERIFICATION_IS_NOT_RECOURSE" in result["non_terminal_warnings"]


def test_verdict_terminal_overclaim_refuses():
    result = inspect_terminal_boundary(load("examples/terminal-overclaim-verdict-fixture.json"))
    assert result["status"] == "REFUSED"
    assert result["accepted"] is False
    assert "TERMINAL_RECOGNITION_OVERCLAIM" in result["blocking_refusals"]
    assert "TERMINAL_RECOURSE_OVERCLAIM" in result["blocking_refusals"]
    assert "RECOURSE_WITHOUT_RECOGNITION" in result["blocking_refusals"]


def test_recognition_fixture_does_not_become_recourse():
    result = inspect_terminal_boundary(load("examples/terminal-recognition-fixture.json"))
    assert result["status"] == "PASS"
    assert result["source_repo"] == "Verifrax/ANAGNORIUM"
    assert result["recognition_terminal"] is True
    assert result["recourse_terminal"] is False
    assert "RECOGNITION_IS_NOT_RECOURSE" in result["non_terminal_warnings"]


def test_recourse_without_recognition_refuses():
    result = inspect_terminal_boundary(load("examples/terminal-recourse-without-recognition-fixture.json"))
    assert result["status"] == "REFUSED"
    assert result["source_repo"] == "Verifrax/REGRESSORIUM"
    assert "RECOURSE_WITHOUT_RECOGNITION" in result["blocking_refusals"]
