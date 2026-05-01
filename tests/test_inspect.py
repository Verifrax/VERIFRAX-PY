from verifrax.inspect import inspect_bundle


def test_incomplete_bundle_refuses():
    result = inspect_bundle("examples/incomplete-bundle.json")
    assert result["verified_boundary_sufficient"] is False
    assert "OBJECT_CHAIN_INCOMPLETE" in result["blocking_refusals"]


def test_minimum_bundle_verifies_but_not_terminal():
    result = inspect_bundle("examples/minimum-verifiable-bundle.json")
    assert result["verified_boundary_sufficient"] is True
    assert result["terminal"] is False
    assert "MISSING_RECOGNITION_OBJECT" in result["non_terminal_warnings"]
