import json
from pathlib import Path

from verifrax.api_contract import assert_api_contract, inspect_api_contract


def test_api_contract_fixture_passes():
    contract = json.loads(Path("examples/api-contract-fixture.json").read_text())
    result = assert_api_contract(contract)
    assert result["status"] == "PASS"
    assert result["accepted"] is True
    assert result["source_repo"] == "Verifrax/VERIFRAX-API"
    assert "/api/receipt/{id}" in result["present_paths"]
    assert "/api/verdict/{id}" in result["present_paths"]


def test_api_contract_missing_path_refuses():
    contract = json.loads(Path("examples/api-contract-fixture.json").read_text())
    contract["paths"].pop("/api/verdict/{id}")
    result = inspect_api_contract(contract).to_dict()
    assert result["status"] == "REFUSED"
    assert result["accepted"] is False
    assert "/api/verdict/{id}" in result["missing_paths"]
    assert any(item.startswith("API_CONTRACT_PATH_MISSING") for item in result["refusals"])
