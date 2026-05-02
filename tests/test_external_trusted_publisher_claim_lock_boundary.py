import json
from pathlib import Path
data=json.loads(Path("EXTERNAL_TRUSTED_PUBLISHER_CLAIMS.json").read_text())
assert data["do_not_publish"] is True
assert data["claim_lock_active"] is True
assert data["testpypi"]["project_name"]=="verifrax"
assert data["testpypi"]["owner"]=="Verifrax"
assert data["testpypi"]["repository"]=="VERIFRAX-PY"
assert data["testpypi"]["workflow_filename"]=="testpypi-publish.yml"
assert data["testpypi"]["environment"]=="testpypi"
assert data["testpypi"]["expected_sub"]=="repo:Verifrax/VERIFRAX-PY:environment:testpypi"
assert data["pypi"]["project_name"]=="verifrax"
assert data["pypi"]["owner"]=="Verifrax"
assert data["pypi"]["repository"]=="VERIFRAX-PY"
assert data["pypi"]["workflow_filename"]=="pypi-publish.yml"
assert data["pypi"]["environment"]=="pypi"
assert data["pypi"]["expected_sub"]=="repo:Verifrax/VERIFRAX-PY:environment:pypi"
text=Path("EXTERNAL_PYPI_CUSTODY_RUNBOOK.md").read_text()
assert "Status: **DO NOT PUBLISH**" in text
assert "Workflow filename: testpypi-publish.yml" in text
assert "Workflow filename: pypi-publish.yml" in text
assert "Environment: testpypi" in text
assert "Environment: pypi" in text
assert "No token publish. No manual upload. No production dispatch before authorization." in text
script=Path("scripts/check-external-trusted-publisher-claim-lock-boundary.py").read_text()
assert "EXTERNAL_TRUSTED_PUBLISHER_CLAIM_LOCK_BOUNDARY" in script
assert "repo:Verifrax/VERIFRAX-PY:environment:testpypi" in script
assert "repo:Verifrax/VERIFRAX-PY:environment:pypi" in script
