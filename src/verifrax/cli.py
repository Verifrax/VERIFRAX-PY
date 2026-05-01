import json
import typer
from rich import print

from . import __version__
from .api import VerifraxClient
from .inspect import inspect_bundle
from .refusal import Refusal
from .verify import verify_path

app = typer.Typer()
api_app = typer.Typer()
bundle_app = typer.Typer()
refusal_app = typer.Typer()

app.add_typer(api_app, name="api")
app.add_typer(bundle_app, name="bundle")
app.add_typer(refusal_app, name="refusal")


def emit(value):
    print(json.dumps(value, indent=2, sort_keys=True))


@app.command()
def doctor():
    emit({
        "package": "verifrax",
        "version": __version__,
        "boundary": "python-sdk-cli-implementation",
        "sovereign_chamber": False,
        "truth_owner": False,
        "status": "OK"
    })


@app.command()
def sources():
    emit({
        "repo": "Verifrax/VERIFRAX-PY",
        "distribution": "verifrax",
        "bindings": ["Verifrax/VERIFRAX", "Verifrax/VERIFRAX-API", "Verifrax/VERIFRAX-verify"]
    })


@app.command()
def verify(path: str):
    emit(verify_path(path))


@api_app.command("health")
def api_health():
    emit(VerifraxClient().health())


@api_app.command("ready")
def api_ready():
    emit(VerifraxClient().ready())


@api_app.command("version")
def api_version():
    emit(VerifraxClient().version())


@api_app.command("openapi")
def api_openapi():
    emit(VerifraxClient().openapi())


@bundle_app.command("inspect")
def bundle_inspect(path: str):
    emit(inspect_bundle(path))


@refusal_app.command("explain")
def refusal_explain(code: str):
    r = Refusal.explain(code)
    emit({"code": r.code.value, "meaning": r.meaning})
