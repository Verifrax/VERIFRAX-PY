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

if pypi_version_exists:
    raise SystemExit(json.dumps({
        "status":"REFUSED",
        "gate":"VERSION_IMMUTABILITY_INDEX_REFUSAL_BOUNDARY",
        "code":"PYPI_VERSION_ALREADY_EXISTS",
        "package":"verifrax",
        "version":"0.1.0",
        "pypi_status":pypi_status,
        "do_not_publish":True
    }, indent=2))

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
    "duplicate_upload_refusal_active":True,
    "production_publish_blocked_if_version_exists":True,
    "no_publish_executed":True
}, indent=2))
