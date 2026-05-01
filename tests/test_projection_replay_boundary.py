import json
from pathlib import Path

from verifrax.projections import inspect_receipt_projection, inspect_verdict_projection


def test_receipt_projection_fixture_passes():
    projection = json.loads(Path("examples/receipt-projection-fixture.json").read_text())
    result = inspect_receipt_projection(projection)
    assert result["status"] == "PASS"
    assert result["accepted"] is True
    assert result["source_repo"] == "Verifrax/CORPIFORM"
    assert result["api_boundary"] == "Verifrax/VERIFRAX-API"
    assert result["package_boundary"] == "Verifrax/VERIFRAX-PY"


def test_verdict_projection_fixture_passes():
    projection = json.loads(Path("examples/verdict-projection-fixture.json").read_text())
    result = inspect_verdict_projection(projection)
    assert result["status"] == "PASS"
    assert result["accepted"] is True
    assert result["source_repo"] == "Verifrax/VERIFRAX"
    assert "VERDICT_IS_NOT_TERMINAL_RECOGNITION" in result["non_terminal_warnings"]


def test_incomplete_receipt_projection_refuses():
    projection = json.loads(Path("examples/incomplete-receipt-projection.json").read_text())
    result = inspect_receipt_projection(projection)
    assert result["status"] == "REFUSED"
    assert result["accepted"] is False
    assert "RECEIPT_PROJECTION_INCOMPLETE" in result["blocking_refusals"]
