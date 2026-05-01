from verifrax.refusal import Refusal


def test_refusal_explain():
    r = Refusal.explain("MISSING_LAW_VERSION")
    assert r.code.value == "MISSING_LAW_VERSION"
