import json
from pathlib import Path


def inspect_bundle(path: str) -> dict:
    data = json.loads(Path(path).read_text())
    present = {
        "law_version": bool(data.get("law_version")),
        "accepted_epoch": bool(data.get("accepted_epoch")),
        "verification_result": bool(data.get("verification_result")),
        "recognition_object": bool(data.get("recognition_object")),
        "recourse_object": bool(data.get("recourse_object"))
    }
    refusals = []
    if not present["law_version"]:
        refusals.append("MISSING_LAW_VERSION")
    if not present["accepted_epoch"]:
        refusals.append("MISSING_ACCEPTED_EPOCH")
    if not present["verification_result"]:
        refusals.append("MISSING_VERIFICATION_RESULT")
    if refusals:
        refusals.append("OBJECT_CHAIN_INCOMPLETE")
    return {"path": path, "present": present, "refusals": refusals}
