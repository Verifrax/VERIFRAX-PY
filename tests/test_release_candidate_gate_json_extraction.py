import importlib.util
from pathlib import Path


def load_gate_module():
    path = Path("scripts/check-release-candidate-attestation-readiness-boundary.py")
    spec = importlib.util.spec_from_file_location("release_gate", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_gate_extracts_json_after_build_logs():
    module = load_gate_module()
    output = """* Creating isolated environment: venv+pip...
* Building wheel...
Successfully built verifrax-0.1.0.tar.gz and verifrax-0.1.0-py3-none-any.whl
{
  "status": "PASS",
  "gate": "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE"
}
"""
    parsed = module.parse_json(output, "TEST")
    assert parsed["status"] == "PASS"
    assert parsed["gate"] == "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE"
