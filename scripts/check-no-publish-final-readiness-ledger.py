import json, subprocess, sys
from pathlib import Path
ROOT=Path.cwd()
ledger=json.loads((ROOT/"NO_PUBLISH_FINAL_READINESS_LEDGER.json").read_text())
assert ledger["status"]=="REPO_SIDE_READY_NO_PUBLISH"
assert ledger["package"]=="verifrax"
assert ledger["version"]=="0.1.0"
assert ledger["source_repo"]=="Verifrax/VERIFRAX-PY"
assert ledger["do_not_publish"] is True
assert ledger["publish_default"]=="REFUSE"
assert ledger["production_publish_state"]=="REFUSED_BY_DESIGN"
assert ledger["production_refusal"]=="PRODUCTION_PYPI_AUTHORIZATION_MISSING"
required=set(ledger["required_gates"])
for gate in [
 "API_MACHINE_CONTRACT_REPLAY_BOUNDARY",
 "RECEIPT_VERDICT_PROJECTION_REPLAY_BOUNDARY",
 "TERMINAL_NONRECOGNITION_NONRECOURSE_GUARD",
 "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE",
 "DISTRIBUTION_INSTALLATION_REPLAY_PROOF",
 "PYTEST_WARNING_FREE_RELEASE_GATE",
 "RELEASE_CANDIDATE_ATTESTATION_READINESS_BOUNDARY",
 "TESTPYPI_REHEARSAL_ATTESTATION_BOUNDARY",
 "V010_RELEASE_ADMISSIBILITY_CLOSURE_BOUNDARY",
 "PYPI_TRUSTED_PUBLISHER_READINESS_SEAL",
 "PRODUCTION_PYPI_PUBLISH_DEADMAN_BOUNDARY",
 "EXTERNAL_TRUSTED_PUBLISHER_CLAIM_LOCK_BOUNDARY",
 "RELEASE_ARTIFACT_DIGEST_REPLAY_BOUNDARY"
]:
    assert gate in required
external=ledger["external_requirements"]
assert external["testpypi_pending_trusted_publisher"]["project_name"]=="verifrax"
assert external["testpypi_pending_trusted_publisher"]["owner"]=="Verifrax"
assert external["testpypi_pending_trusted_publisher"]["repository"]=="VERIFRAX-PY"
assert external["testpypi_pending_trusted_publisher"]["workflow_filename"]=="testpypi-publish.yml"
assert external["testpypi_pending_trusted_publisher"]["environment"]=="testpypi"
assert external["pypi_pending_trusted_publisher"]["project_name"]=="verifrax"
assert external["pypi_pending_trusted_publisher"]["owner"]=="Verifrax"
assert external["pypi_pending_trusted_publisher"]["repository"]=="VERIFRAX-PY"
assert external["pypi_pending_trusted_publisher"]["workflow_filename"]=="pypi-publish.yml"
assert external["pypi_pending_trusted_publisher"]["environment"]=="pypi"
assert external["testpypi_live_rehearsal_required"] is True
assert external["production_authorization_required"] is True
for forbidden in [
 "manual_token_publish",
 "twine_upload",
 "long_lived_api_token_publish"
]:
    assert forbidden in ledger["forbidden_until_external_requirements_satisfied"]
scripts=[
 "scripts/check-api-machine-contract-replay-boundary.py",
 "scripts/check-receipt-verdict-projection-replay-boundary.py",
 "scripts/check-terminal-nonrecognition-nonrecourse-guard.py",
 "scripts/check-pypi-custody-attestation-release-gate.py",
 "scripts/check-distribution-installation-replay-proof.py",
 "scripts/check-pytest-warning-free-release-gate.py",
 "scripts/check-release-candidate-attestation-readiness-boundary.py",
 "scripts/check-testpypi-rehearsal-attestation-boundary.py",
 "scripts/check-v010-release-admissibility-closure-boundary.py",
 "scripts/check-pypi-trusted-publisher-readiness-seal.py",
 "scripts/check-production-pypi-publish-deadman-boundary.py",
 "scripts/check-external-trusted-publisher-claim-lock-boundary.py",
 "scripts/check-release-artifact-digest-replay-boundary.py"
]
for script in scripts:
    assert (ROOT/script).exists(), script
for script in [
 "scripts/check-release-artifact-digest-replay-boundary.py",
 "scripts/check-external-trusted-publisher-claim-lock-boundary.py",
 "scripts/check-production-pypi-publish-deadman-boundary.py",
 "scripts/check-pypi-trusted-publisher-readiness-seal.py",
 "scripts/check-v010-release-admissibility-closure-boundary.py"
]:
    subprocess.check_call([sys.executable, script], cwd=ROOT)
print(json.dumps({
 "status":"PASS",
 "gate":"NO_PUBLISH_FINAL_READINESS_LEDGER",
 "package":"verifrax",
 "version":"0.1.0",
 "source_repo":"Verifrax/VERIFRAX-PY",
 "repo_side_ready":True,
 "do_not_publish":True,
 "publish_default":"REFUSE",
 "production_publish_state":"REFUSED_BY_DESIGN",
 "production_refusal":"PRODUCTION_PYPI_AUTHORIZATION_MISSING",
 "external_configuration_required":True,
 "no_publish_executed":True
}, indent=2))
