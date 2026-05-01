import json
from pathlib import Path

from verifrax.release import release_readiness


def test_release_candidate_manifest():
    data = json.loads(Path("RELEASE_CANDIDATE.json").read_text())
    assert data["package"] == "verifrax"
    assert data["version"] == "0.1.0"
    assert data["source_repo"] == "Verifrax/VERIFRAX-PY"
    assert "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE" in data["required_gates"]
    assert "DISTRIBUTION_INSTALLATION_REPLAY_PROOF" in data["required_gates"]
    assert "UNATTESTED_PUBLISH" in data["forbidden_release_states"]


def test_release_readiness_passes():
    result = release_readiness()
    assert result["status"] == "PASS"
    assert result["accepted"] is True
    assert result["blocking_refusals"] == []
    assert result["source_repo"] == "Verifrax/VERIFRAX-PY"


def test_release_readiness_script_exists():
    script = Path("scripts/check-release-candidate-attestation-readiness-boundary.py")
    assert script.exists()
    text = script.read_text()
    assert "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY" in text
    assert "check-terminal-nonrecognition-nonrecourse-guard.py" in text
