import json, re, urllib.error, urllib.request
from pathlib import Path

ROOT=Path.cwd()
policy=json.loads((ROOT/"VERSION_IMMUTABILITY_INDEX_REFUSAL.json").read_text())
assert policy["package"]=="verifrax"
assert policy["version"]=="0.1.0"
assert policy["source_repo"]=="Verifrax/VERIFRAX-PY"
assert policy["do_not_publish"] is True
assert policy["publish_default"]=="REFUSE"
assert policy["immutable_indices"]["pypi"]["refuse_duplicate_upload"] is True
assert policy["immutable_indices"]["testpypi"]["refuse_duplicate_upload"] is True
assert "PYPI_VERSION_ALREADY_EXISTS" in policy["required_refusals"]
assert "skip_existing_publish" in policy["forbidden"]

def fetch(url):
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"verifrax-py-no-publish-index-probe"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 404, ""
        raise

def has_version(html, version):
    return bool(re.search(rf'verifrax-{re.escape(version)}(?:-|\.tar\.gz)', html, re.I))

testpypi_status, testpypi_html = fetch(policy["immutable_indices"]["testpypi"]["simple_index"])
pypi_status, pypi_html = fetch(policy["immutable_indices"]["pypi"]["simple_index"])

testpypi_version_exists = testpypi_status == 200 and has_version(testpypi_html, policy["version"])
pypi_version_exists = pypi_status == 200 and has_version(pypi_html, policy["version"])

seal_path = ROOT/"evidence/pypi-production-publish-v0.1.0/PRODUCTION_PYPI_V010_SEAL.json"
production_seal_active = False
production_publish_state = "PRE_PRODUCTION_UNPUBLISHED"

if pypi_version_exists:
    if not seal_path.exists():
        raise SystemExit(json.dumps({
            "status":"REFUSED",
            "gate":"VERSION_IMMUTABILITY_INDEX_REFUSAL_BOUNDARY",
            "code":"PYPI_VERSION_ALREADY_EXISTS_WITHOUT_REPO_SEAL",
            "package":"verifrax",
            "version":"0.1.0",
            "pypi_status":pypi_status,
            "do_not_publish":True
        }, indent=2))

    seal = json.loads(seal_path.read_text())
    assert seal["status"] == "PASS"
    assert seal["gate"] == "PRODUCTION_PYPI_V010_SEAL"
    assert seal["package"] == "verifrax"
    assert seal["version"] == "0.1.0"
    assert seal["source_repo"] == "Verifrax/VERIFRAX-PY"
    assert seal["production_publish"] == "DONE"
    assert seal["production_external_install_replay"] == "DONE"
    assert seal["version_immutability"] == "SEALED"
    assert seal["do_not_rerun_same_version_publish"] is True
    production_seal_active = True
    production_publish_state = "SEALED_ALREADY_PUBLISHED"

print(json.dumps({
    "status":"PASS",
    "gate":"VERSION_IMMUTABILITY_INDEX_REFUSAL_BOUNDARY",
    "package":"verifrax",
    "version":"0.1.0",
    "source_repo":"Verifrax/VERIFRAX-PY",
    "do_not_publish":True,
    "publish_default":"REFUSE",
    "pypi_version_exists":pypi_version_exists,
    "testpypi_version_exists":testpypi_version_exists,
    "production_seal_active":production_seal_active,
    "production_publish_state":production_publish_state,
    "duplicate_upload_refusal_active":True,
    "production_publish_blocked_if_version_exists":True,
    "same_version_publish_rerun_refused":pypi_version_exists and production_seal_active,
    "no_publish_executed":True
}, indent=2))
