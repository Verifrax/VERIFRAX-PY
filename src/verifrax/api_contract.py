from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ApiContractRefusalCode(str, Enum):
    API_CONTRACT_MISSING = "API_CONTRACT_MISSING"
    API_CONTRACT_OPENAPI_VERSION_MISSING = "API_CONTRACT_OPENAPI_VERSION_MISSING"
    API_CONTRACT_PATH_MISSING = "API_CONTRACT_PATH_MISSING"
    API_CONTRACT_METHOD_MISSING = "API_CONTRACT_METHOD_MISSING"
    API_CONTRACT_OPERATION_ID_MISSING = "API_CONTRACT_OPERATION_ID_MISSING"


REQUIRED_API_OPERATIONS: dict[str, dict[str, str]] = {
    "/healthz": {"method": "get", "operation_id": "healthz"},
    "/readyz": {"method": "get", "operation_id": "readyz"},
    "/version": {"method": "get", "operation_id": "version"},
    "/openapi.json": {"method": "get", "operation_id": "openapi"},
    "/api/receipt/{id}": {"method": "get", "operation_id": "getReceipt"},
    "/api/verdict/{id}": {"method": "get", "operation_id": "getVerdict"},
}


@dataclass(frozen=True)
class ApiContractInspection:
    status: str
    openapi: str | None
    required_paths: list[str]
    present_paths: list[str]
    missing_paths: list[str]
    refusals: list[str]
    source_repo: str = "Verifrax/VERIFRAX-API"
    package_repo: str = "Verifrax/VERIFRAX-PY"

    @property
    def accepted(self) -> bool:
        return not self.refusals

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "accepted": self.accepted,
            "openapi": self.openapi,
            "source_repo": self.source_repo,
            "package_repo": self.package_repo,
            "required_paths": self.required_paths,
            "present_paths": self.present_paths,
            "missing_paths": self.missing_paths,
            "refusals": self.refusals,
        }


def inspect_api_contract(contract: dict[str, Any]) -> ApiContractInspection:
    refusals: list[str] = []

    openapi = contract.get("openapi")
    if not openapi:
        refusals.append(ApiContractRefusalCode.API_CONTRACT_OPENAPI_VERSION_MISSING.value)

    paths = contract.get("paths")
    if not isinstance(paths, dict):
        return ApiContractInspection(
            status="REFUSED",
            openapi=openapi,
            required_paths=list(REQUIRED_API_OPERATIONS),
            present_paths=[],
            missing_paths=list(REQUIRED_API_OPERATIONS),
            refusals=[
                ApiContractRefusalCode.API_CONTRACT_MISSING.value,
                ApiContractRefusalCode.API_CONTRACT_PATH_MISSING.value,
            ],
        )

    present_paths = sorted(path for path in REQUIRED_API_OPERATIONS if path in paths)
    missing_paths = sorted(path for path in REQUIRED_API_OPERATIONS if path not in paths)

    for path in missing_paths:
        refusals.append(f"{ApiContractRefusalCode.API_CONTRACT_PATH_MISSING.value}:{path}")

    for path, expected in REQUIRED_API_OPERATIONS.items():
        if path not in paths:
            continue
        method = expected["method"]
        operation_id = expected["operation_id"]
        path_item = paths.get(path) or {}
        operation = path_item.get(method)
        if not isinstance(operation, dict):
            refusals.append(f"{ApiContractRefusalCode.API_CONTRACT_METHOD_MISSING.value}:{path}:{method}")
            continue
        if operation.get("operationId") != operation_id:
            refusals.append(f"{ApiContractRefusalCode.API_CONTRACT_OPERATION_ID_MISSING.value}:{path}:{operation_id}")

    return ApiContractInspection(
        status="PASS" if not refusals else "REFUSED",
        openapi=openapi,
        required_paths=list(REQUIRED_API_OPERATIONS),
        present_paths=present_paths,
        missing_paths=missing_paths,
        refusals=refusals,
    )


def assert_api_contract(contract: dict[str, Any]) -> dict[str, Any]:
    inspection = inspect_api_contract(contract)
    return inspection.to_dict()
