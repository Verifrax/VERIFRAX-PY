import pytest
from verifrax.refusal import Refusal, RefusalCode, refusal_codes


def test_refusal_explain():
    refusal = Refusal.explain("MISSING_LAW_VERSION")
    assert refusal.code is RefusalCode.MISSING_LAW_VERSION
    assert refusal.severity == "BLOCKING"
    assert "law version" in refusal.meaning


def test_refusal_list_contains_object_chain():
    assert "OBJECT_CHAIN_INCOMPLETE" in refusal_codes()


def test_unknown_refusal_rejected():
    with pytest.raises(ValueError):
        Refusal.explain("NOT_A_REFUSAL")
