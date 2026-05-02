import json
from pathlib import Path
policy=json.loads(Path("RELEASE_ARTIFACT_DIGEST_BOUNDARY.json").read_text())
assert policy["package"]=="verifrax"
assert policy["version"]=="0.1.0"
assert policy["source_repo"]=="Verifrax/VERIFRAX-PY"
assert policy["do_not_publish"] is True
assert policy["publish_default"]=="REFUSE"
assert policy["external_publishers_required"] is True
assert policy["production_authorization_required"] is True
script=Path("scripts/check-release-artifact-digest-replay-boundary.py").read_text()
assert "RELEASE_ARTIFACT_DIGEST_REPLAY_BOUNDARY" in script
assert "sha256" in script
assert "no_publish_executed" in script
