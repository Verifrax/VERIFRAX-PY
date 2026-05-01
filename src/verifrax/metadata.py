from __future__ import annotations

from importlib.metadata import PackageNotFoundError, metadata, version


def package_metadata() -> dict[str, str]:
    try:
        dist = metadata("verifrax")
        package_version = version("verifrax")
        return {
            "name": dist.get("Name", "verifrax"),
            "version": package_version,
            "summary": dist.get("Summary", ""),
        }
    except PackageNotFoundError:
        return {
            "name": "verifrax",
            "version": "0.1.0",
            "summary": "local editable source tree",
        }
