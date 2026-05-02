import json, sys
from pathlib import Path
ROOT=Path.cwd()
claims=json.loads((ROOT/"EXTERNAL_TRUSTED_PUBLISHER_CLAIMS.json").read_text())
runbook=(ROOT/"EXTERNAL_PYPI_CUSTODY_RUNBOOK.md").read_text()
testpypi_workflow=(ROOT/".github/workflows/testpypi-publish.yml").read_text()
pypi_workflow=(ROOT/".github/workflows/pypi-publish.yml").read_text()
trusted=json.loads((ROOT/"PYPI_TRUSTED_PUBLISHER_READINESS.json").read_text())
deadman=json.loads((ROOT/"PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_POLICY.json").read_text())
assert claims["do_not_publish"] is True
assert claims["claim_lock_active"] is True
assert claims["testpypi"]["project_name"]=="verifrax"
assert claims["testpypi"]["owner"]=="Verifrax"
assert claims["testpypi"]["repository"]=="VERIFRAX-PY"
assert claims["testpypi"]["workflow_filename"]=="testpypi-publish.yml"
assert claims["testpypi"]["environment"]=="testpypi"
assert claims["testpypi"]["expected_sub"]=="repo:Verifrax/VERIFRAX-PY:environment:testpypi"
assert claims["testpypi"]["expected_workflow_ref"]=="Verifrax/VERIFRAX-PY/.github/workflows/testpypi-publish.yml@refs/heads/main"
assert claims["pypi"]["project_name"]=="verifrax"
assert claims["pypi"]["owner"]=="Verifrax"
assert claims["pypi"]["repository"]=="VERIFRAX-PY"
assert claims["pypi"]["workflow_filename"]=="pypi-publish.yml"
assert claims["pypi"]["environment"]=="pypi"
assert claims["pypi"]["expected_sub"]=="repo:Verifrax/VERIFRAX-PY:environment:pypi"
assert claims["pypi"]["expected_workflow_ref"]=="Verifrax/VERIFRAX-PY/.github/workflows/pypi-publish.yml@refs/heads/main"
assert "Status: **DO NOT PUBLISH**" in runbook
assert "Workflow filename: testpypi-publish.yml" in runbook
assert "Workflow filename: pypi-publish.yml" in runbook
assert "Environment: testpypi" in runbook
assert "Environment: pypi" in runbook
assert "No token publish. No manual upload. No production dispatch before authorization." in runbook
assert "workflow_dispatch" in testpypi_workflow
assert "id-token: write" in testpypi_workflow
assert "environment: testpypi" in testpypi_workflow
assert "test.pypi.org/legacy" in testpypi_workflow
assert "python scripts/check-pypi-trusted-publisher-readiness-seal.py" in testpypi_workflow
assert "workflow_dispatch" in pypi_workflow
assert "id-token: write" in pypi_workflow
assert "environment: pypi" in pypi_workflow
assert "python scripts/check-production-pypi-publish-authorization-boundary.py" in pypi_workflow
assert "uses: pypa/gh-action-pypi-publish@release/v1" in pypi_workflow
assert trusted["do_not_publish"] is True
assert deadman["production_publish_default"]=="REFUSE"
print(json.dumps({"status":"PASS","gate":"EXTERNAL_TRUSTED_PUBLISHER_CLAIM_LOCK_BOUNDARY","package":"verifrax","version":"0.1.0","source_repo":"Verifrax/VERIFRAX-PY","do_not_publish":True,"testpypi_claim_lock":claims,"pypi_claim_lock":claims,"production_publish_default":"REFUSE","external_configuration_required":True,"no_publish_executed":True}, indent=2))
