from __future__ import annotations


def attestation_status() -> dict[str, object]:
    return {
        "pypi_attestation_required": True,
        "trusted_publishing_required": True,
        "runtime_attestation_verification": "not_available_in_0.1.0",
    }
