from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def fail(code: str, message: str) -> None:
    print(json.dumps({
        "status": "REFUSED",
        "gate": "DISTRIBUTION_INSTALLATION_REPLAY_PROOF",
        "code": code,
        "message": message,
    }, indent=2))
    raise SystemExit(1)


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )


def clean_dist() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)


def build_distribution() -> tuple[Path, Path]:
    clean_dist()
    run([sys.executable, "-m", "build"])
    wheels = sorted(DIST.glob("verifrax-*.whl"))
    sdists = sorted(DIST.glob("verifrax-*.tar.gz"))
    if len(wheels) != 1:
        fail("WHEEL_COUNT_INVALID", f"expected exactly one wheel, found {len(wheels)}")
    if len(sdists) != 1:
        fail("SDIST_COUNT_INVALID", f"expected exactly one sdist, found {len(sdists)}")
    return wheels[0], sdists[0]


def write_bundle(path: Path) -> None:
    path.write_text(json.dumps({
        "claim_class": "distribution-installation-replay-proof",
        "law_version": "",
        "accepted_epoch": "",
        "verification_result": ""
    }, indent=2) + "\n", encoding="utf-8")


def assert_output_contains(output: str, needle: str, code: str) -> None:
    if needle not in output:
        fail(code, f"missing expected output: {needle}\n{output}")


def verify_installed_artifact(artifact: Path, label: str) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix=f"verifrax-{label}-install-") as tmp:
        tmp_path = Path(tmp)
        venv = tmp_path / ".venv"
        bundle = tmp_path / "incomplete-bundle.json"
        write_bundle(bundle)

        run([sys.executable, "-m", "venv", str(venv)])

        python = venv / "bin" / "python"
        pip = venv / "bin" / "pip"
        cli = venv / "bin" / "verifrax"

        run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
        run([str(pip), "install", str(artifact)])

        import_check = run([
            str(python),
            "-c",
            "import verifrax; print(verifrax.__version__); print(verifrax.__all__)"
        ]).stdout
        assert_output_contains(import_check, "0.1.0", f"{label.upper()}_IMPORT_VERSION_MISSING")
        assert_output_contains(import_check, "VerifraxClient", f"{label.upper()}_IMPORT_SURFACE_MISSING")

        doctor = run([str(cli), "doctor"]).stdout
        assert_output_contains(doctor, "\"package\": \"verifrax\"", f"{label.upper()}_CLI_DOCTOR_PACKAGE_MISSING")
        assert_output_contains(doctor, "\"sovereign_chamber\": false", f"{label.upper()}_CLI_DOCTOR_BOUNDARY_MISSING")

        sources = run([str(cli), "sources"]).stdout
        assert_output_contains(sources, "Verifrax/VERIFRAX-PY", f"{label.upper()}_SOURCE_REPO_MISSING")
        assert_output_contains(sources, "SYNTAGMARIUM", f"{label.upper()}_NON_BINDING_MISSING")

        policy = run([str(cli), "policy"]).stdout
        assert_output_contains(policy, "\"truth_owner\": false", f"{label.upper()}_POLICY_TRUTH_OWNER_MISSING")
        assert_output_contains(policy, "\"package_default\": true", f"{label.upper()}_POLICY_PACKAGE_DEFAULT_MISSING")

        refusal = run([str(cli), "refusal", "explain", "OBJECT_CHAIN_INCOMPLETE"]).stdout
        assert_output_contains(refusal, "\"severity\": \"BLOCKING\"", f"{label.upper()}_REFUSAL_SEVERITY_MISSING")
        assert_output_contains(refusal, "The object chain is incomplete.", f"{label.upper()}_REFUSAL_MEANING_MISSING")

        inspection = run([str(cli), "bundle", "inspect", str(bundle)]).stdout
        assert_output_contains(inspection, "OBJECT_CHAIN_INCOMPLETE", f"{label.upper()}_BUNDLE_REFUSAL_MISSING")
        assert_output_contains(inspection, "\"verified_boundary_sufficient\": false", f"{label.upper()}_BUNDLE_BOUNDARY_RESULT_MISSING")

        return {
            "artifact": artifact.name,
            "label": label,
            "doctor": "PASS",
            "sources": "PASS",
            "policy": "PASS",
            "refusal": "PASS",
            "bundle_inspect": "PASS",
            "import_surface": "PASS",
        }


def main() -> None:
    wheel, sdist = build_distribution()
    wheel_result = verify_installed_artifact(wheel, "wheel")
    sdist_result = verify_installed_artifact(sdist, "sdist")

    print(json.dumps({
        "status": "PASS",
        "gate": "DISTRIBUTION_INSTALLATION_REPLAY_PROOF",
        "project": "verifrax",
        "source_repo": "Verifrax/VERIFRAX-PY",
        "wheel": wheel_result,
        "sdist": sdist_result,
    }, indent=2))


if __name__ == "__main__":
    main()
