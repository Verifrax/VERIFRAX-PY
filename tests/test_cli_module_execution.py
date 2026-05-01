import json
import subprocess
import sys


def test_cli_module_execution_emits_json():
    output = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "verifrax.cli",
            "api-contract",
            "inspect",
            "examples/api-contract-fixture.json",
        ],
        text=True,
    )
    data = json.loads(output)
    assert data["status"] == "PASS"
    assert data["accepted"] is True
    assert data["source_repo"] == "Verifrax/VERIFRAX-API"
    assert data["package_repo"] == "Verifrax/VERIFRAX-PY"
