from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .refusal import RefusalCode


_REQUIRED_FOR_VERIFICATION = {
    "law_version": RefusalCode.MISSING_LAW_VERSION,
    "accepted_epoch": RefusalCode.MISSING_ACCEPTED_EPOCH,
    "verification_result": RefusalCode.MISSING_VERIFICATION_RESULT,
}

_OPTIONAL_TERMINAL = {
    "authority_object": RefusalCode.MISSING_AUTHORITY_OBJECT,
    "execution_receipt": RefusalCode.MISSING_EXECUTION_RECEIPT,
    "recognition_object": RefusalCode.MISSING_RECOGNITION_OBJECT,
    "recourse_object": RefusalCode.MISSING_RECOURSE_OBJECT,
}


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def inspect_bundle(path: str | Path) -> dict[str, Any]:
    data = load_json(path)
    present = {
        key: bool(data.get(key))
        for key in [
            "claim_class",
            "law_version",
            "accepted_epoch",
            "authority_object",
            "execution_receipt",
            "verification_result",
            "recognition_object",
            "recourse_object",
        ]
    }

    blocking: list[str] = []
    warnings: list[str] = []

    if not present["claim_class"]:
        blocking.append(RefusalCode.UNSUPPORTED_CLAIM_CLASS.value)

    for key, code in _REQUIRED_FOR_VERIFICATION.items():
        if not present[key]:
            blocking.append(code.value)

    for key, code in _OPTIONAL_TERMINAL.items():
        if not present[key]:
            warnings.append(code.value)

    if blocking:
        blocking.append(RefusalCode.OBJECT_CHAIN_INCOMPLETE.value)

    return {
        "path": str(path),
        "present": present,
        "blocking_refusals": blocking,
        "non_terminal_warnings": warnings,
        "verified_boundary_sufficient": not blocking,
        "terminal": bool(present["recognition_object"] and present["recourse_object"]),
    }
