import json, subprocess, sys
from pathlib import Path
ROOT=Path.cwd()
seal=json.loads((ROOT/"PYPI_TRUSTED_PUBLISHER_READINESS.json").read_text())
custody=json.loads((ROOT/"PYPI_CUSTODY.json").read_text())
testpypi_workflow=(ROOT/".github/workflows/testpypi-publish.yml").read_text()
pypi_workflow=(ROOT/".github/workflows/pypi-publish.yml").read_text()
assert seal["do_not_publish"] is True
assert seal["production_publish_blocked_until_external_trusted_publishers_exist"] is True
assert seal["testpypi"]["project_name"]=="verifrax"
assert seal["testpypi"]["owner"]=="Verifrax"
assert seal["testpypi"]["repository"]=="VERIFRAX-PY"
assert seal["testpypi"]["workflow_filename"]=="testpypi-publish.yml"
assert seal["testpypi"]["environment"]=="testpypi"
assert seal["testpypi"]["oidc_sub"]=="repo:Verifrax/VERIFRAX-PY:environment:testpypi"
assert seal["pypi"]["project_name"]=="verifrax"
assert seal["pypi"]["owner"]=="Verifrax"
assert seal["pypi"]["repository"]=="VERIFRAX-PY"
assert seal["pypi"]["workflow_filename"]=="pypi-publish.yml"
assert seal["pypi"]["environment"]=="pypi"
assert seal["pypi"]["oidc_sub"]=="repo:Verifrax/VERIFRAX-PY:environment:pypi"
assert (ROOT/"EXTERNAL_TRUSTED_PUBLISHER_CLAIMS.json").exists()
assert (ROOT/"EXTERNAL_PYPI_CUSTODY_RUNBOOK.md").exists()
assert (ROOT/"PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_POLICY.json").exists()
assert (ROOT/"scripts/check-production-pypi-publish-authorization-boundary.py").exists()
assert (ROOT/"scripts/check-production-pypi-publish-deadman-boundary.py").exists()
assert (ROOT/"scripts/check-external-trusted-publisher-claim-lock-boundary.py").exists()
assert "workflow_dispatch" in testpypi_workflow
assert "id-token: write" in testpypi_workflow
assert "environment: testpypi" in testpypi_workflow
assert "test.pypi.org/legacy" in testpypi_workflow
assert "python scripts/check-pypi-trusted-publisher-readiness-seal.py" in testpypi_workflow
assert "python scripts/check-v010-release-admissibility-closure-boundary.py" in testpypi_workflow
assert "workflow_dispatch" in pypi_workflow
assert "id-token: write" in pypi_workflow
assert "environment: pypi" in pypi_workflow
assert "python scripts/check-production-pypi-publish-authorization-boundary.py" in pypi_workflow
assert "python scripts/check-pypi-trusted-publisher-readiness-seal.py" in pypi_workflow
assert "python scripts/check-v010-release-admissibility-closure-boundary.py" in pypi_workflow
assert custody["trusted_publisher_readiness"]["status"]=="DECLARED_NOT_PUBLISHED"
assert custody["trusted_publisher_readiness"]["do_not_publish"] is True
req=custody["release_requirements"]
assert req["testpypi_pending_trusted_publisher_required"] is True
assert req["pypi_pending_trusted_publisher_required"] is True
assert req["do_not_publish_without_testpypi_live_rehearsal_proof"] is True
assert req["production_pypi_publish_deadman_required"] is True
assert req["production_pypi_publish_authorization_required"] is True
assert req["testpypi_live_rehearsal_proof_required"] is True
assert req["production_publish_default_refuse"] is True
assert req["external_trusted_publisher_claim_lock_required"] is True
subprocess.check_call([sys.executable,"scripts/check-v010-release-admissibility-closure-boundary.py"], cwd=ROOT)
subprocess.check_call([sys.executable,"scripts/check-production-pypi-publish-deadman-boundary.py"], cwd=ROOT)
subprocess.check_call([sys.executable,"scripts/check-external-trusted-publisher-claim-lock-boundary.py"], cwd=ROOT)
print(json.dumps({"status":"PASS","gate":"PYPI_TRUSTED_PUBLISHER_READINESS_SEAL","package":"verifrax","version":"0.1.0","source_repo":"Verifrax/VERIFRAX-PY","do_not_publish":True,"testpypi_pending_trusted_publisher":{"owner":"Verifrax","repository":"VERIFRAX-PY","workflow":"testpypi-publish.yml","environment":"testpypi"},"pypi_pending_trusted_publisher":{"owner":"Verifrax","repository":"VERIFRAX-PY","workflow":"pypi-publish.yml","environment":"pypi"},"repo_side_ready":True,"external_publishers_still_manual":True,"production_publish_deadman_active":True,"production_publish_default":"REFUSE","external_claim_lock_active":True}, indent=2))
