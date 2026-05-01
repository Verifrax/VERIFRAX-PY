from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("Python 3.11+ required for tomllib", file=sys.stderr)
    raise


ROOT = Path(__file__).resolve().parents[1]


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def load_json(path: str) -> dict:
    p = ROOT / path
    if not p.exists():
        fail("MISSING_RELEASE_GATE_OBJECT", f"missing {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    pyproject_path = ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        fail("MISSING_PYPROJECT", "pyproject.toml is required")

    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = pyproject.get("project", {})

    if project.get("name") != "verifrax":
        fail("PYPI_PROJECT_MISMATCH", "project.name must be verifrax")

    if project.get("license") != "Apache-2.0":
        fail("PACKAGE_LICENSE_MISMATCH", "project.license must be Apache-2.0")

    if project.get("requires-python") != ">=3.10":
        fail("PYTHON_REQUIRES_MISMATCH", "requires-python must be >=3.10")

    scripts = project.get("scripts", {})
    if scripts.get("verifrax") != "verifrax.cli:app":
        fail("CLI_ENTRYPOINT_MISMATCH", "verifrax CLI must bind to verifrax.cli:app")

    custody = load_json("PYPI_CUSTODY.json")
    if custody.get("pypi_project") != "verifrax":
        fail("PYPI_CUSTODY_PROJECT_MISMATCH", "PYPI_CUSTODY pypi_project must be verifrax")

    if custody.get("source_repo") != "Verifrax/VERIFRAX-PY":
        fail("PYPI_CUSTODY_SOURCE_MISMATCH", "PYPI_CUSTODY source_repo must be Verifrax/VERIFRAX-PY")

    publisher = custody.get("publisher", {})
    if publisher.get("method") != "pypi-trusted-publishing":
        fail("PYPI_PUBLISHER_METHOD_MISMATCH", "Trusted Publishing is required")

    if publisher.get("oidc_provider") != "github-actions":
        fail("PYPI_OIDC_PROVIDER_MISMATCH", "GitHub Actions OIDC is required")

    if publisher.get("workflow") != ".github/workflows/pypi-publish.yml":
        fail("PYPI_WORKFLOW_MISMATCH", "pypi-publish workflow binding mismatch")

    if publisher.get("environment") != "pypi":
        fail("PYPI_ENVIRONMENT_MISMATCH", "pypi environment binding mismatch")

    release_requirements = custody.get("release_requirements", {})
    required_true = [
        "trusted_publishing_required",
        "attestation_required",
        "sdist_required",
        "wheel_required",
        "testpypi_rehearsal_required",
        "refusal_tests_required",
        "source_binding_check_required",
        "cli_smoke_required",
    ]
    missing_true = [key for key in required_true if release_requirements.get(key) is not True]
    if missing_true:
        fail("PYPI_RELEASE_REQUIREMENT_MISSING", ",".join(missing_true))

    forbidden = set(custody.get("forbidden", []))
    for item in {
        "manual_password_publish",
        "long_lived_token_publish",
        "unattested_release",
        "source_repo_mismatch",
        "empty_namespace_reservation",
        "sovereign_chamber_distribution",
    }:
        if item not in forbidden:
            fail("PYPI_FORBIDDEN_CLASS_MISSING", item)

    source_bindings = load_json("SOURCE_BINDINGS.json")
    if source_bindings.get("repo") != "Verifrax/VERIFRAX-PY":
        fail("SOURCE_BINDING_REPO_MISMATCH", "SOURCE_BINDINGS repo mismatch")

    if source_bindings.get("distribution") != "verifrax":
        fail("SOURCE_BINDING_DISTRIBUTION_MISMATCH", "SOURCE_BINDINGS distribution mismatch")

    non_bindings = source_bindings.get("non_bindings", {})
    for required_non_binding in [
        "SYNTAGMARIUM",
        "ORBISTIUM",
        "CONSONORIUM",
        "TACHYRIUM",
        "AUCTORISEAL",
        "CORPIFORM",
        "ANAGNORIUM",
        "REGRESSORIUM",
        "ADMISSORIUM",
    ]:
        if required_non_binding not in non_bindings.values():
            fail("NON_BINDING_MISSING", required_non_binding)

    package_boundary = load_json("PACKAGE_BOUNDARY.json")
    if package_boundary.get("not_sovereignty") is not True:
        fail("PACKAGE_SOVEREIGNTY_OVERCLAIM", "package must explicitly declare not_sovereignty=true")

    if package_boundary.get("package_truth_subordinate") is not True:
        fail("PACKAGE_TRUTH_OVERCLAIM", "package truth must be subordinate")

    refusal_policy = load_json("REFUSAL_POLICY.json")
    if refusal_policy.get("default_behavior") != "REFUSE_UNLESS_OBJECT_CHAIN_SUFFICIENT":
        fail("REFUSAL_DEFAULT_MISMATCH", "default refusal behavior mismatch")

    refusal_codes = {entry.get("code") for entry in refusal_policy.get("refusals", [])}
    for code in [
        "OBJECT_CHAIN_INCOMPLETE",
        "PYPI_ATTESTATION_MISSING",
        "SOURCE_REPO_MISMATCH",
        "MISSING_RECOGNITION_OBJECT",
        "MISSING_RECOURSE_OBJECT",
    ]:
        if code not in refusal_codes:
            fail("REFUSAL_CODE_MISSING", code)

    dist = ROOT / "dist"
    if dist.exists():
        for child in dist.iterdir():
            child.unlink()
    else:
        dist.mkdir()

    run([sys.executable, "-m", "build"])

    wheels = sorted(dist.glob("verifrax-*.whl"))
    sdists = sorted(dist.glob("verifrax-*.tar.gz"))

    if len(wheels) != 1:
        fail("WHEEL_COUNT_INVALID", f"expected 1 wheel, found {len(wheels)}")

    if len(sdists) != 1:
        fail("SDIST_COUNT_INVALID", f"expected 1 sdist, found {len(sdists)}")

    wheel = wheels[0]
    sdist = sdists[0]

    with zipfile.ZipFile(wheel) as zf:
        wheel_names = set(zf.namelist())
        required_wheel_members = {
            "verifrax/__init__.py",
            "verifrax/cli.py",
            "verifrax/refusal.py",
            "verifrax/inspect.py",
            "verifrax/py.typed",
        }
        missing = [name for name in required_wheel_members if name not in wheel_names]
        if missing:
            fail("WHEEL_MEMBER_MISSING", ",".join(missing))

        metadata_names = [name for name in wheel_names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            fail("WHEEL_METADATA_INVALID", "wheel metadata missing or ambiguous")
        metadata = zf.read(metadata_names[0]).decode("utf-8")
        for needle in [
            "Name: verifrax",
            "Version: 0.1.0",
            "License-Expression: Apache-2.0",
            "Requires-Python: >=3.10",
        ]:
            if needle not in metadata:
                fail("WHEEL_METADATA_MISMATCH", needle)

    with tarfile.open(sdist, "r:gz") as tf:
        names = set(tf.getnames())
        required_suffixes = [
            "pyproject.toml",
            "README.md",
            "src/verifrax/cli.py",
            "src/verifrax/refusal.py",
        ]
        for suffix in required_suffixes:
            if not any(name.endswith(suffix) for name in names):
                fail("SDIST_MEMBER_MISSING", suffix)

    print(json.dumps({
        "status": "PASS",
        "gate": "PYPI_CUSTODY_ATTESTATION_RELEASE_GATE",
        "project": "verifrax",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "trusted_publishing_required": True,
        "attestation_required": True,
        "wheel": wheel.name,
        "sdist": sdist.name,
    }, indent=2))


if __name__ == "__main__":
    main()
