from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from . import __version__
from .api import VerifraxClient
from .api_contract import assert_api_contract
from .attestations import attestation_status
from .inspect import inspect_bundle
from .metadata import package_metadata
from .policy import PACKAGE_BOUNDARY
from .projections import inspect_receipt_projection, inspect_verdict_projection
from .refusal import Refusal, refusal_codes
from .terminal import inspect_terminal_boundary
from .verify import verify_path

app = typer.Typer(help="VERIFRAX Python SDK and CLI boundary.")
api_app = typer.Typer(help="Query VERIFRAX API machine-contract surfaces.")
api_contract_app = typer.Typer(help="Inspect VERIFRAX API machine-contract documents.")
receipt_app = typer.Typer(help="Read receipt projections.")
verdict_app = typer.Typer(help="Read verdict projections.")
bundle_app = typer.Typer(help="Inspect local bundles.")
refusal_app = typer.Typer(help="Explain refusal codes.")
self_app = typer.Typer(help="Inspect this package boundary.")
terminal_app = typer.Typer(help="Inspect terminal recognition and recourse boundaries.")

app.add_typer(api_app, name="api")
app.add_typer(api_contract_app, name="api-contract")
app.add_typer(receipt_app, name="receipt")
app.add_typer(verdict_app, name="verdict")
app.add_typer(bundle_app, name="bundle")
app.add_typer(refusal_app, name="refusal")
app.add_typer(self_app, name="self")
app.add_typer(terminal_app, name="terminal")


def emit(value: object) -> None:
    typer.echo(json.dumps(value, indent=2, sort_keys=True))


@app.command()
def doctor() -> None:
    emit({
        "package": "verifrax",
        "version": __version__,
        "boundary": "python-sdk-cli-implementation",
        "repo": "Verifrax/VERIFRAX-PY",
        "sovereign_chamber": False,
        "truth_owner": False,
        "status": "OK",
    })


@app.command()
def sources() -> None:
    emit({
        "repo": "Verifrax/VERIFRAX-PY",
        "distribution": "verifrax",
        "bindings": [
            "Verifrax/VERIFRAX",
            "Verifrax/VERIFRAX-API",
            "Verifrax/VERIFRAX-verify",
            "Verifrax/proof",
            "Verifrax/SIGILLARIUM"
        ],
        "non_bindings": [
            "SYNTAGMARIUM",
            "ORBISTIUM",
            "CONSONORIUM",
            "TACHYRIUM",
            "AUCTORISEAL",
            "CORPIFORM",
            "ANAGNORIUM",
            "REGRESSORIUM",
            "ADMISSORIUM"
        ]
    })


@app.command()
def policy() -> None:
    emit(PACKAGE_BOUNDARY)


@app.command()
def verify(path: str) -> None:
    emit(verify_path(path))


@api_app.command("health")
def api_health(base_url: Optional[str] = None) -> None:
    emit(VerifraxClient(base_url or "https://api.verifrax.net").health())


@api_app.command("ready")
def api_ready(base_url: Optional[str] = None) -> None:
    emit(VerifraxClient(base_url or "https://api.verifrax.net").ready())


@api_app.command("version")
def api_version(base_url: Optional[str] = None) -> None:
    emit(VerifraxClient(base_url or "https://api.verifrax.net").version())


@api_app.command("openapi")
def api_openapi(base_url: Optional[str] = None) -> None:
    emit(VerifraxClient(base_url or "https://api.verifrax.net").openapi())


@receipt_app.command("get")
def receipt_get(receipt_id: str, base_url: Optional[str] = None) -> None:
    emit(VerifraxClient(base_url or "https://api.verifrax.net").receipt(receipt_id))




@receipt_app.command("inspect")
def receipt_inspect(path: str) -> None:
    projection = json.loads(Path(path).read_text(encoding="utf-8"))
    emit(inspect_receipt_projection(projection))


@verdict_app.command("get")
def verdict_get(verdict_id: str, base_url: Optional[str] = None) -> None:
    emit(VerifraxClient(base_url or "https://api.verifrax.net").verdict(verdict_id))




@verdict_app.command("inspect")
def verdict_inspect(path: str) -> None:
    projection = json.loads(Path(path).read_text(encoding="utf-8"))
    emit(inspect_verdict_projection(projection))


@bundle_app.command("inspect")
def bundle_inspect(path: str) -> None:
    emit(inspect_bundle(path))


@refusal_app.command("list")
def refusal_list() -> None:
    emit({"refusals": refusal_codes()})


@refusal_app.command("explain")
def refusal_explain(code: str) -> None:
    refusal = Refusal.explain(code)
    emit({"code": refusal.code.value, "meaning": refusal.meaning, "severity": refusal.severity})


@self_app.command("metadata")
def self_metadata() -> None:
    emit(package_metadata() | {"source_repo": "Verifrax/VERIFRAX-PY"})


@self_app.command("attest")
def self_attest() -> None:
    emit(attestation_status())


@api_contract_app.command("inspect")
def api_contract_inspect(path: str) -> None:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    emit(assert_api_contract(contract))


@terminal_app.command("inspect")
def terminal_inspect(path: str) -> None:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    emit(inspect_terminal_boundary(obj))


if __name__ == "__main__":
    app()
