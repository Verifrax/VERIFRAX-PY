import json
from pathlib import Path


def test_publish_workflow_order_lock_boundary():
    policy = json.loads(Path("PUBLISH_WORKFLOW_ORDER_LOCK.json").read_text())
    prod = Path(".github/workflows/pypi-publish.yml").read_text()

    assert policy["do_not_publish"] is True
    assert policy["publish_default"] == "REFUSE"

    required = [
        "scripts/check-version-immutability-index-refusal-boundary.py",
        "scripts/check-external-trusted-publisher-claim-lock-boundary.py",
        "scripts/check-production-pypi-publish-authorization-boundary.py",
        "scripts/check-production-pypi-publish-deadman-boundary.py",
        "scripts/check-pypi-trusted-publisher-readiness-seal.py",
        "scripts/check-publish-workflow-order-lock-boundary.py",
        "pypa/gh-action-pypi-publish@release/v1",
        "repository-url: https://upload.pypi.org/legacy/",
        "attestations: true",
    ]

    for token in required:
        assert token in prod

    build_pos = prod.index("python -m build")
    publish_pos = prod.index("pypa/gh-action-pypi-publish@release/v1")

    assert prod.index("scripts/check-version-immutability-index-refusal-boundary.py") < build_pos
    assert prod.index("scripts/check-external-trusted-publisher-claim-lock-boundary.py") < build_pos
    assert prod.index("scripts/check-production-pypi-publish-authorization-boundary.py") < build_pos
    assert prod.index("scripts/check-production-pypi-publish-deadman-boundary.py") < publish_pos

    assert "skip-existing: true" not in prod
    assert "password:" not in prod
    assert "TWINE_PASSWORD" not in prod
