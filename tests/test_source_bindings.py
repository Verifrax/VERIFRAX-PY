import json
from pathlib import Path


def test_source_bindings():
    data = json.loads(Path("SOURCE_BINDINGS.json").read_text())
    assert data["repo"] == "Verifrax/VERIFRAX-PY"
    assert data["distribution"] == "verifrax"
    assert data["bindings"]["api_contract_boundary"] == "Verifrax/VERIFRAX-API"
    assert data["non_bindings"]["law"] == "SYNTAGMARIUM"
