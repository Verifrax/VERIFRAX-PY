from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProjectionRefusalCode(str, Enum):
    PROJECTION_SCHEMA_MISSING = "PROJECTION_SCHEMA_MISSING"
    PROJECTION_TYPE_MISSING = "PROJECTION_TYPE_MISSING"
    PROJECTION_SOURCE_REPO_MISSING = "PROJECTION_SOURCE_REPO_MISSING"
    PROJECTION_SOURCE_REPO_MISMATCH = "PROJECTION_SOURCE_REPO_MISMATCH"
    PROJECTION_API_BOUNDARY_MISSING = "PROJECTION_API_BOUNDARY_MISSING"
    PROJECTION_API_BOUNDARY_MISMATCH = "PROJECTION_API_BOUNDARY_MISMATCH"
    PROJECTION_PACKAGE_BOUNDARY_MISSING = "PROJECTION_PACKAGE_BOUNDARY_MISSING"
    PROJECTION_PACKAGE_BOUNDARY_MISMATCH = "PROJECTION_PACKAGE_BOUNDARY_MISMATCH"
    RECEIPT_ID_MISSING = "RECEIPT_ID_MISSING"
    RECEIPT_AUTHORITY_OBJECT_MISSING = "RECEIPT_AUTHORITY_OBJECT_MISSING"
    RECEIPT_EXECUTION_OBJECT_MISSING = "RECEIPT_EXECUTION_OBJECT_MISSING"
    RECEIPT_PROJECTION_INCOMPLETE = "RECEIPT_PROJECTION_INCOMPLETE"
    VERDICT_ID_MISSING = "VERDICT_ID_MISSING"
    VERDICT_VERIFICATION_RESULT_MISSING = "VERDICT_VERIFICATION_RESULT_MISSING"
    VERDICT_RECOGNITION_BOUNDARY_MISSING = "VERDICT_RECOGNITION_BOUNDARY_MISSING"
    VERDICT_RECOURSE_BOUNDARY_MISSING = "VERDICT_RECOURSE_BOUNDARY_MISSING"
    VERDICT_PROJECTION_INCOMPLETE = "VERDICT_PROJECTION_INCOMPLETE"


@dataclass(frozen=True)
class ProjectionInspection:
    status: str
    projection_kind: str
    accepted: bool
    source_repo: str | None
    api_boundary: str | None
    package_boundary: str | None
    blocking_refusals: list[str]
    non_terminal_warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "projection_kind": self.projection_kind,
            "accepted": self.accepted,
            "source_repo": self.source_repo,
            "api_boundary": self.api_boundary,
            "package_boundary": self.package_boundary,
            "blocking_refusals": self.blocking_refusals,
            "non_terminal_warnings": self.non_terminal_warnings,
        }


def _common_refusals(
    projection: dict[str, Any],
    *,
    expected_schema: str,
    expected_projection_type: str,
    expected_source_repo: str,
) -> list[str]:
    refusals: list[str] = []

    if projection.get("schema") != expected_schema:
        refusals.append(ProjectionRefusalCode.PROJECTION_SCHEMA_MISSING.value)

    if projection.get("projection_type") != expected_projection_type:
        refusals.append(ProjectionRefusalCode.PROJECTION_TYPE_MISSING.value)

    source_repo = projection.get("source_repo")
    if not source_repo:
        refusals.append(ProjectionRefusalCode.PROJECTION_SOURCE_REPO_MISSING.value)
    elif source_repo != expected_source_repo:
        refusals.append(ProjectionRefusalCode.PROJECTION_SOURCE_REPO_MISMATCH.value)

    api_boundary = projection.get("api_boundary")
    if not api_boundary:
        refusals.append(ProjectionRefusalCode.PROJECTION_API_BOUNDARY_MISSING.value)
    elif api_boundary != "Verifrax/VERIFRAX-API":
        refusals.append(ProjectionRefusalCode.PROJECTION_API_BOUNDARY_MISMATCH.value)

    package_boundary = projection.get("package_boundary")
    if not package_boundary:
        refusals.append(ProjectionRefusalCode.PROJECTION_PACKAGE_BOUNDARY_MISSING.value)
    elif package_boundary != "Verifrax/VERIFRAX-PY":
        refusals.append(ProjectionRefusalCode.PROJECTION_PACKAGE_BOUNDARY_MISMATCH.value)

    return refusals


def inspect_receipt_projection(projection: dict[str, Any]) -> dict[str, Any]:
    refusals = _common_refusals(
        projection,
        expected_schema="verifrax.receipt-projection.v1",
        expected_projection_type="EXECUTION_RECEIPT_PROJECTION",
        expected_source_repo="Verifrax/CORPIFORM",
    )

    if not projection.get("receipt_id"):
        refusals.append(ProjectionRefusalCode.RECEIPT_ID_MISSING.value)

    if not projection.get("authority_object"):
        refusals.append(ProjectionRefusalCode.RECEIPT_AUTHORITY_OBJECT_MISSING.value)

    if not projection.get("execution"):
        refusals.append(ProjectionRefusalCode.RECEIPT_EXECUTION_OBJECT_MISSING.value)

    if refusals:
        refusals.append(ProjectionRefusalCode.RECEIPT_PROJECTION_INCOMPLETE.value)

    return ProjectionInspection(
        status="PASS" if not refusals else "REFUSED",
        projection_kind="EXECUTION_RECEIPT_PROJECTION",
        accepted=not refusals,
        source_repo=projection.get("source_repo"),
        api_boundary=projection.get("api_boundary"),
        package_boundary=projection.get("package_boundary"),
        blocking_refusals=refusals,
        non_terminal_warnings=[
            "RECEIPT_IS_NOT_TERMINAL_RECOGNITION",
            "RECEIPT_IS_NOT_TERMINAL_RECOURSE",
        ],
    ).to_dict()


def inspect_verdict_projection(projection: dict[str, Any]) -> dict[str, Any]:
    refusals = _common_refusals(
        projection,
        expected_schema="verifrax.verdict-projection.v1",
        expected_projection_type="VERIFICATION_VERDICT_PROJECTION",
        expected_source_repo="Verifrax/VERIFRAX",
    )

    if not projection.get("verdict_id"):
        refusals.append(ProjectionRefusalCode.VERDICT_ID_MISSING.value)

    if not projection.get("verification_result"):
        refusals.append(ProjectionRefusalCode.VERDICT_VERIFICATION_RESULT_MISSING.value)

    if not projection.get("recognition_boundary"):
        refusals.append(ProjectionRefusalCode.VERDICT_RECOGNITION_BOUNDARY_MISSING.value)

    if not projection.get("recourse_boundary"):
        refusals.append(ProjectionRefusalCode.VERDICT_RECOURSE_BOUNDARY_MISSING.value)

    if refusals:
        refusals.append(ProjectionRefusalCode.VERDICT_PROJECTION_INCOMPLETE.value)

    return ProjectionInspection(
        status="PASS" if not refusals else "REFUSED",
        projection_kind="VERIFICATION_VERDICT_PROJECTION",
        accepted=not refusals,
        source_repo=projection.get("source_repo"),
        api_boundary=projection.get("api_boundary"),
        package_boundary=projection.get("package_boundary"),
        blocking_refusals=refusals,
        non_terminal_warnings=[
            "VERDICT_IS_NOT_TERMINAL_RECOGNITION",
            "VERDICT_IS_NOT_TERMINAL_RECOURSE",
        ],
    ).to_dict()
