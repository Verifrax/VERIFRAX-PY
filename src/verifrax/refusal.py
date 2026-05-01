from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RefusalCode(str, Enum):
    UNSUPPORTED_CLAIM_CLASS = "UNSUPPORTED_CLAIM_CLASS"
    MISSING_LAW_VERSION = "MISSING_LAW_VERSION"
    MISSING_ACCEPTED_EPOCH = "MISSING_ACCEPTED_EPOCH"
    MISSING_AUTHORITY_OBJECT = "MISSING_AUTHORITY_OBJECT"
    MISSING_EXECUTION_RECEIPT = "MISSING_EXECUTION_RECEIPT"
    MISSING_VERIFICATION_RESULT = "MISSING_VERIFICATION_RESULT"
    MISSING_RECOGNITION_OBJECT = "MISSING_RECOGNITION_OBJECT"
    MISSING_RECOURSE_OBJECT = "MISSING_RECOURSE_OBJECT"
    HOST_ROLE_MISMATCH = "HOST_ROLE_MISMATCH"
    SOURCE_REPO_MISMATCH = "SOURCE_REPO_MISMATCH"
    PYPI_ATTESTATION_MISSING = "PYPI_ATTESTATION_MISSING"
    OBJECT_CHAIN_INCOMPLETE = "OBJECT_CHAIN_INCOMPLETE"


_REFUSAL_MEANINGS = {
    RefusalCode.UNSUPPORTED_CLAIM_CLASS: "The inspected claim class is not admitted by this package boundary.",
    RefusalCode.MISSING_LAW_VERSION: "No governing law version was available.",
    RefusalCode.MISSING_ACCEPTED_EPOCH: "No accepted epoch or accepted state was available.",
    RefusalCode.MISSING_AUTHORITY_OBJECT: "No authority object was available.",
    RefusalCode.MISSING_EXECUTION_RECEIPT: "No execution receipt was available.",
    RefusalCode.MISSING_VERIFICATION_RESULT: "No verification result was available.",
    RefusalCode.MISSING_RECOGNITION_OBJECT: "Terminal recognition cannot be inferred from verification alone.",
    RefusalCode.MISSING_RECOURSE_OBJECT: "Terminal recourse cannot be inferred from recognition absence.",
    RefusalCode.HOST_ROLE_MISMATCH: "A host or route did not match its declared role.",
    RefusalCode.SOURCE_REPO_MISMATCH: "The package source binding does not match the admitted repo.",
    RefusalCode.PYPI_ATTESTATION_MISSING: "Required PyPI publish attestation was not available.",
    RefusalCode.OBJECT_CHAIN_INCOMPLETE: "The object chain is incomplete.",
}


@dataclass(frozen=True)
class Refusal:
    code: RefusalCode
    meaning: str
    severity: str = "BLOCKING"

    @classmethod
    def explain(cls, code: str) -> "Refusal":
        parsed = RefusalCode(code)
        severity = "NON_TERMINAL" if parsed in {
            RefusalCode.MISSING_RECOGNITION_OBJECT,
            RefusalCode.MISSING_RECOURSE_OBJECT,
        } else "BLOCKING"
        return cls(code=parsed, meaning=_REFUSAL_MEANINGS[parsed], severity=severity)


def refusal_codes() -> list[str]:
    return [code.value for code in RefusalCode]
