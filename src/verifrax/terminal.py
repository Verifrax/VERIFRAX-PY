from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TerminalRefusalCode(str, Enum):
    TERMINAL_SCHEMA_MISSING = "TERMINAL_SCHEMA_MISSING"
    TERMINAL_PROJECTION_TYPE_MISSING = "TERMINAL_PROJECTION_TYPE_MISSING"
    TERMINAL_SOURCE_REPO_MISSING = "TERMINAL_SOURCE_REPO_MISSING"
    TERMINAL_SOURCE_REPO_MISMATCH = "TERMINAL_SOURCE_REPO_MISMATCH"
    TERMINAL_API_BOUNDARY_MISMATCH = "TERMINAL_API_BOUNDARY_MISMATCH"
    TERMINAL_PACKAGE_BOUNDARY_MISMATCH = "TERMINAL_PACKAGE_BOUNDARY_MISMATCH"
    VERIFICATION_IS_NOT_RECOGNITION = "VERIFICATION_IS_NOT_RECOGNITION"
    VERIFICATION_IS_NOT_RECOURSE = "VERIFICATION_IS_NOT_RECOURSE"
    TERMINAL_RECOGNITION_OVERCLAIM = "TERMINAL_RECOGNITION_OVERCLAIM"
    TERMINAL_RECOURSE_OVERCLAIM = "TERMINAL_RECOURSE_OVERCLAIM"
    RECOGNITION_OBJECT_MISSING = "RECOGNITION_OBJECT_MISSING"
    RECOURSE_OBJECT_MISSING = "RECOURSE_OBJECT_MISSING"
    RECOURSE_WITHOUT_RECOGNITION = "RECOURSE_WITHOUT_RECOGNITION"


@dataclass(frozen=True)
class TerminalInspection:
    status: str
    accepted: bool
    terminal_kind: str
    source_repo: str | None
    api_boundary: str | None
    package_boundary: str | None
    recognition_terminal: bool
    recourse_terminal: bool
    blocking_refusals: list[str]
    non_terminal_warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "accepted": self.accepted,
            "terminal_kind": self.terminal_kind,
            "source_repo": self.source_repo,
            "api_boundary": self.api_boundary,
            "package_boundary": self.package_boundary,
            "recognition_terminal": self.recognition_terminal,
            "recourse_terminal": self.recourse_terminal,
            "blocking_refusals": self.blocking_refusals,
            "non_terminal_warnings": self.non_terminal_warnings,
        }


def _boundary_refusals(obj: dict[str, Any], expected_source_repo: str) -> list[str]:
    refusals: list[str] = []

    source_repo = obj.get("source_repo")
    if not source_repo:
        refusals.append(TerminalRefusalCode.TERMINAL_SOURCE_REPO_MISSING.value)
    elif source_repo != expected_source_repo:
        refusals.append(TerminalRefusalCode.TERMINAL_SOURCE_REPO_MISMATCH.value)

    if obj.get("api_boundary") != "Verifrax/VERIFRAX-API":
        refusals.append(TerminalRefusalCode.TERMINAL_API_BOUNDARY_MISMATCH.value)

    if obj.get("package_boundary") != "Verifrax/VERIFRAX-PY":
        refusals.append(TerminalRefusalCode.TERMINAL_PACKAGE_BOUNDARY_MISMATCH.value)

    return refusals


def inspect_terminal_boundary(obj: dict[str, Any]) -> dict[str, Any]:
    projection_type = obj.get("projection_type")
    schema = obj.get("schema")

    if projection_type == "VERIFICATION_VERDICT_PROJECTION":
        refusals = _boundary_refusals(obj, "Verifrax/VERIFRAX")
        warnings = [
            TerminalRefusalCode.VERIFICATION_IS_NOT_RECOGNITION.value,
            TerminalRefusalCode.VERIFICATION_IS_NOT_RECOURSE.value,
        ]

        recognition_terminal = obj.get("recognition_boundary") == "TERMINAL_RECOGNITION"
        recourse_terminal = obj.get("recourse_boundary") == "TERMINAL_RECOURSE"

        if recognition_terminal and not obj.get("recognition_object"):
            refusals.append(TerminalRefusalCode.TERMINAL_RECOGNITION_OVERCLAIM.value)
            refusals.append(TerminalRefusalCode.RECOGNITION_OBJECT_MISSING.value)

        if recourse_terminal and not obj.get("recourse_object"):
            refusals.append(TerminalRefusalCode.TERMINAL_RECOURSE_OVERCLAIM.value)
            refusals.append(TerminalRefusalCode.RECOURSE_OBJECT_MISSING.value)

        if recourse_terminal and not obj.get("recognition_object"):
            refusals.append(TerminalRefusalCode.RECOURSE_WITHOUT_RECOGNITION.value)

        return TerminalInspection(
            status="PASS" if not refusals else "REFUSED",
            accepted=not refusals,
            terminal_kind="VERIFICATION_VERDICT_PROJECTION",
            source_repo=obj.get("source_repo"),
            api_boundary=obj.get("api_boundary"),
            package_boundary=obj.get("package_boundary"),
            recognition_terminal=False if not recognition_terminal else bool(obj.get("recognition_object")),
            recourse_terminal=False if not recourse_terminal else bool(obj.get("recourse_object")),
            blocking_refusals=refusals,
            non_terminal_warnings=warnings,
        ).to_dict()

    if projection_type == "TERMINAL_RECOGNITION_PROJECTION":
        refusals = _boundary_refusals(obj, "Verifrax/ANAGNORIUM")
        if schema != "verifrax.terminal-recognition.v1":
            refusals.append(TerminalRefusalCode.TERMINAL_SCHEMA_MISSING.value)
        if not obj.get("recognition_object"):
            refusals.append(TerminalRefusalCode.RECOGNITION_OBJECT_MISSING.value)

        return TerminalInspection(
            status="PASS" if not refusals else "REFUSED",
            accepted=not refusals,
            terminal_kind="TERMINAL_RECOGNITION_PROJECTION",
            source_repo=obj.get("source_repo"),
            api_boundary=obj.get("api_boundary"),
            package_boundary=obj.get("package_boundary"),
            recognition_terminal=not refusals,
            recourse_terminal=False,
            blocking_refusals=refusals,
            non_terminal_warnings=["RECOGNITION_IS_NOT_RECOURSE"],
        ).to_dict()

    if projection_type == "TERMINAL_RECOURSE_PROJECTION":
        refusals = _boundary_refusals(obj, "Verifrax/REGRESSORIUM")
        if schema != "verifrax.terminal-recourse.v1":
            refusals.append(TerminalRefusalCode.TERMINAL_SCHEMA_MISSING.value)
        if not obj.get("recourse_object"):
            refusals.append(TerminalRefusalCode.RECOURSE_OBJECT_MISSING.value)
        if not obj.get("recognition_object"):
            refusals.append(TerminalRefusalCode.RECOURSE_WITHOUT_RECOGNITION.value)

        return TerminalInspection(
            status="PASS" if not refusals else "REFUSED",
            accepted=not refusals,
            terminal_kind="TERMINAL_RECOURSE_PROJECTION",
            source_repo=obj.get("source_repo"),
            api_boundary=obj.get("api_boundary"),
            package_boundary=obj.get("package_boundary"),
            recognition_terminal=bool(obj.get("recognition_object")),
            recourse_terminal=not refusals,
            blocking_refusals=refusals,
            non_terminal_warnings=[],
        ).to_dict()

    return TerminalInspection(
        status="REFUSED",
        accepted=False,
        terminal_kind=str(projection_type or "UNKNOWN"),
        source_repo=obj.get("source_repo"),
        api_boundary=obj.get("api_boundary"),
        package_boundary=obj.get("package_boundary"),
        recognition_terminal=False,
        recourse_terminal=False,
        blocking_refusals=[
            TerminalRefusalCode.TERMINAL_PROJECTION_TYPE_MISSING.value
        ],
        non_terminal_warnings=[],
    ).to_dict()
