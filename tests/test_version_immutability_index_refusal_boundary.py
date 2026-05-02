import json
from pathlib import Path

policy=json.loads(Path("VERSION_IMMUTABILITY_INDEX_REFUSAL.json").read_text())
assert policy["package"]=="verifrax"
assert policy["version"]=="0.1.0"
assert policy["do_not_publish"] is True
assert policy["publish_default"]=="REFUSE"
assert policy["immutable_indices"]["pypi"]["version_must_not_exist_before_production_publish"] is True
assert policy["immutable_indices"]["testpypi"]["version_may_exist_after_live_rehearsal"] is True
assert "PYPI_VERSION_ALREADY_EXISTS" in policy["required_refusals"]
assert "blind_publish_without_index_probe" in policy["forbidden"]
script=Path("scripts/check-version-immutability-index-refusal-boundary.py").read_text()
assert "VERSION_IMMUTABILITY_INDEX_REFUSAL_BOUNDARY" in script
assert "PYPI_VERSION_ALREADY_EXISTS" in script
assert "no_publish_executed" in script
