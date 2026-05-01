from __future__ import annotations

from pathlib import Path
from typing import Any

from .inspect import inspect_bundle


def verify_path(path: str | Path) -> dict[str, Any]:
    inspection = inspect_bundle(path)
    return {
        "verified": inspection["verified_boundary_sufficient"],
        "terminal": inspection["terminal"],
        "inspection": inspection,
    }
