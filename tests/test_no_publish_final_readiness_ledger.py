import json
from pathlib import Path
ledger=json.loads(Path("NO_PUBLISH_FINAL_READINESS_LEDGER.json").read_text())
assert ledger["status"]=="REPO_SIDE_READY_NO_PUBLISH"
assert ledger["do_not_publish"] is True
assert ledger["publish_default"]=="REFUSE"
assert ledger["production_publish_state"]=="REFUSED_BY_DESIGN"
assert ledger["production_refusal"]=="PRODUCTION_PYPI_AUTHORIZATION_MISSING"
assert "RELEASE_ARTIFACT_DIGEST_REPLAY_BOUNDARY" in ledger["required_gates"]
assert "EXTERNAL_TRUSTED_PUBLISHER_CLAIM_LOCK_BOUNDARY" in ledger["required_gates"]
assert "PRODUCTION_PYPI_PUBLISH_DEADMAN_BOUNDARY" in ledger["required_gates"]
assert ledger["external_requirements"]["testpypi_pending_trusted_publisher"]["environment"]=="testpypi"
assert ledger["external_requirements"]["pypi_pending_trusted_publisher"]["environment"]=="pypi"
assert "twine_upload" in ledger["forbidden_until_external_requirements_satisfied"]
script=Path("scripts/check-no-publish-final-readiness-ledger.py").read_text()
assert "NO_PUBLISH_FINAL_READINESS_LEDGER" in script
assert "no_publish_executed" in script
