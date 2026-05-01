import json
import tomllib
from pathlib import Path


def test_pyproject_identity():
    data = tomllib.loads(Path("pyproject.toml").read_text())
    assert data["project"]["name"] == "verifrax"
    assert data["project"]["license"] == "Apache-2.0"


def test_custody_forbids_tokens():
    data = json.loads(Path("PYPI_CUSTODY.json").read_text())
    assert "long_lived_token_publish" in data["forbidden"]
    assert data["publisher"]["method"] == "pypi-trusted-publishing"
