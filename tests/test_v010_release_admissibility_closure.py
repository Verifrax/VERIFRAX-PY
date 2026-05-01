import json
from pathlib import Path


def test_v010_release_candidate_declares_all_release_gates():
    data = json.loads(Path("RELEASE_CANDIDATE.json").read_text())
    required = {
        "API_MACHINE_CONTRACT_REPLAY_BOUNDARY",
        "RECEIPT_VERDICT_PROJECTION_REPLAY_BOUNDARY",
        "TERMINAL_NONRECOGNITION_NONRECOURSE_GUARD",
        "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE",
        "DISTRIBUTION_INSTALLATION_REPLAY_PROOF",
        "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
        "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY",
        "PYTEST_WARNING_FREE_RELEASE_GATE",
    }
    assert required.issubset(set(data["required_gates"]))


def test_v010_pypi_custody_declares_all_release_flags():
    data = json.loads(Path("PYPI_CUSTODY.json").read_text())
    req = data["release_requirements"]
    assert req["release_candidate_readiness_required"] is True
    assert req["testpypi_rehearsal_required"] is True
    assert req["pytest_warning_free_required"] is True
    assert req["terminal_nonrecognition_nonrecourse_guard_required"] is True
    assert req["receipt_verdict_projection_replay_required"] is True
    assert req["api_machine_contract_replay_required"] is True


def test_v010_release_admissibility_closure_gate_exists():
    script = Path("scripts/check-v010-release-admissibility-closure-boundary.py")
    assert script.exists()
    text = script.read_text()
    assert "V010_RELEASE_ADMISSIBILITY_CLOSURE_BOUNDARY" in text
    assert "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY" in text
    assert "PYTEST_WARNING_FREE_RELEASE_GATE" in text
    assert "VERIFRAX_RELEASE_GATE_NO_NESTED" in text
