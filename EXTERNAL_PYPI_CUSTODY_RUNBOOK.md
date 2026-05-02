# VERIFRAX-PY External PyPI Custody Runbook

Status: **DO NOT PUBLISH**

Repo-side readiness is sealed. Public publishing remains externally blocked until TestPyPI and PyPI trusted publishers exist with exact claims.

## TestPyPI pending trusted publisher

Create exactly:

```text
Project name: verifrax
Owner: Verifrax
Repository: VERIFRAX-PY
Workflow filename: testpypi-publish.yml
Environment: testpypi
````

Expected claims:

```text
sub: repo:Verifrax/VERIFRAX-PY:environment:testpypi
repository: Verifrax/VERIFRAX-PY
repository_owner: Verifrax
workflow_ref: Verifrax/VERIFRAX-PY/.github/workflows/testpypi-publish.yml@refs/heads/main
ref: refs/heads/main
environment: testpypi
```

Allowed command after external TestPyPI setup:

```bash
gh workflow run testpypi-publish.yml --repo Verifrax/VERIFRAX-PY --ref main
```

Install proof command:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ verifrax==0.1.0
```

## Production PyPI pending trusted publisher

Create exactly:

```text
Project name: verifrax
Owner: Verifrax
Repository: VERIFRAX-PY
Workflow filename: pypi-publish.yml
Environment: pypi
```

Expected claims:

```text
sub: repo:Verifrax/VERIFRAX-PY:environment:pypi
repository: Verifrax/VERIFRAX-PY
repository_owner: Verifrax
workflow_ref: Verifrax/VERIFRAX-PY/.github/workflows/pypi-publish.yml@refs/heads/main
ref: refs/heads/main
environment: pypi
```

Production remains blocked until all are true:

```text
TESTPYPI_LIVE_REHEARSAL_PROOF_BOUNDARY=PASS
PYPI_PRODUCTION_PUBLISH_AUTHORIZATION.json exists
PRODUCTION_PYPI_PUBLISH_AUTHORIZATION_BOUNDARY=PASS
PRODUCTION_PYPI_PUBLISH_DEADMAN_BOUNDARY=PASS
```

No token publish. No manual upload. No production dispatch before authorization.
