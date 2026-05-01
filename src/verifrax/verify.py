from .inspect import inspect_bundle


def verify_path(path: str) -> dict:
    inspection = inspect_bundle(path)
    return {"verified": not inspection["refusals"], "inspection": inspection}
