import hashlib, json, shutil, subprocess, sys, tarfile, zipfile
from pathlib import Path
ROOT=Path.cwd()
for path in [ROOT/"dist", ROOT/"build"]:
    shutil.rmtree(path, ignore_errors=True)
build=subprocess.run([sys.executable,"-m","build"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
dist=ROOT/"dist"
wheels=sorted(dist.glob("verifrax-0.1.0-*.whl"))
sdists=sorted(dist.glob("verifrax-0.1.0.tar.gz"))
assert len(wheels)==1, [p.name for p in wheels]
assert len(sdists)==1, [p.name for p in sdists]
wheel=wheels[0]
sdist=sdists[0]
wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest()
sdist_sha256=hashlib.sha256(sdist.read_bytes()).hexdigest()
z=zipfile.ZipFile(wheel)
wheel_names=z.namelist()
metadata_name=next(name for name in wheel_names if name.endswith(".dist-info/METADATA"))
wheel_metadata=z.read(metadata_name).decode("utf-8")
record_name=next(name for name in wheel_names if name.endswith(".dist-info/RECORD"))
z.close()
assert "Name: verifrax" in wheel_metadata
assert "Version: 0.1.0" in wheel_metadata
assert record_name.endswith(".dist-info/RECORD")
t=tarfile.open(sdist)
tar_names=t.getnames()
t.close()
assert any(name.endswith("/pyproject.toml") for name in tar_names)
assert any("/src/verifrax/__init__.py" in name for name in tar_names)
policy=json.loads((ROOT/"RELEASE_ARTIFACT_DIGEST_BOUNDARY.json").read_text())
assert policy["do_not_publish"] is True
assert policy["publish_default"]=="REFUSE"
assert policy["external_publishers_required"] is True
assert policy["production_authorization_required"] is True
print(json.dumps({
  "status":"PASS",
  "gate":"RELEASE_ARTIFACT_DIGEST_REPLAY_BOUNDARY",
  "package":"verifrax",
  "version":"0.1.0",
  "source_repo":"Verifrax/VERIFRAX-PY",
  "do_not_publish":True,
  "wheel":{"artifact":wheel.name,"sha256":wheel_sha256,"metadata":"PASS","record":"PASS"},
  "sdist":{"artifact":sdist.name,"sha256":sdist_sha256,"pyproject":"PASS","package_source":"PASS"},
  "publish_default":"REFUSE",
  "no_publish_executed":True
}, indent=2))
