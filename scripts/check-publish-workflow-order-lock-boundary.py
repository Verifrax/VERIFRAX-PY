import json
from pathlib import Path

ROOT = Path.cwd()
policy = json.loads((ROOT / "PUBLISH_WORKFLOW_ORDER_LOCK.json").read_text())

prod_path = ROOT / policy["production_workflow"]
test_path = ROOT / policy["testpypi_workflow"]
prod = prod_path.read_text()
testpypi = test_path.read_text()

assert policy["package"] == "verifrax"
assert policy["version"] == "0.1.0"
assert policy["source_repo"] == "Verifrax/VERIFRAX-PY"
assert policy["do_not_publish"] is True
assert policy["publish_default"] == "REFUSE"

for token in policy["required_publish_semantics"]:
    assert token in prod, token

assert "workflow_dispatch:" in testpypi
assert "environment: testpypi" in testpypi
assert "repository-url: https://test.pypi.org/legacy/" in testpypi
assert "attestations: true" in testpypi

for forbidden in policy["forbidden_publish_semantics"]:
    assert forbidden not in prod, forbidden
    assert forbidden not in testpypi, forbidden

build_markers = [
    "python -m build",
    "python -m build --sdist --wheel",
]
build_pos = min((prod.find(m) for m in build_markers if m in prod), default=-1)
assert build_pos >= 0, "production build step not found"

publish_pos = prod.find("pypa/gh-action-pypi-publish")
assert publish_pos >= 0, "production publish action not found"

for gate in policy["required_before_build"]:
    pos = prod.find(gate)
    assert pos >= 0, f"missing before-build gate: {gate}"
    assert pos < build_pos, f"gate must precede build: {gate}"

for gate in policy["required_before_publish"]:
    pos = prod.find(gate)
    assert pos >= 0, f"missing before-publish gate: {gate}"
    assert pos < publish_pos, f"gate must precede publish action: {gate}"

assert prod.find("scripts/check-production-pypi-publish-authorization-boundary.py") < publish_pos
assert prod.find("scripts/check-production-pypi-publish-deadman-boundary.py") < publish_pos
assert prod.find("scripts/check-version-immutability-index-refusal-boundary.py") < build_pos

print(json.dumps({
    "status": "PASS",
    "gate": "PUBLISH_WORKFLOW_ORDER_LOCK_BOUNDARY",
    "package": "verifrax",
    "version": "0.1.0",
    "source_repo": "Verifrax/VERIFRAX-PY",
    "do_not_publish": True,
    "publish_default": "REFUSE",
    "production_workflow_manual_only": True,
    "version_index_refusal_before_build": True,
    "external_claim_lock_before_build": True,
    "authorization_before_build": True,
    "authorization_before_publish": True,
    "deadman_before_publish": True,
    "trusted_publisher_readiness_before_publish": True,
    "token_publish_forbidden": True,
    "skip_existing_forbidden": True,
    "no_publish_executed": True
}, indent=2))
