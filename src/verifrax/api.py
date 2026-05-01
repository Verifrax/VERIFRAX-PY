from typing import Any
import httpx


class VerifraxClient:
    def __init__(self, base_url: str = "https://api.verifrax.net", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str) -> Any:
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            response = client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            if "application/json" in response.headers.get("content-type", ""):
                return response.json()
            return response.text

    def health(self) -> Any:
        return self._get("/healthz")

    def ready(self) -> Any:
        return self._get("/readyz")

    def version(self) -> Any:
        return self._get("/version")

    def openapi(self) -> Any:
        return self._get("/openapi.json")

    def receipt(self, receipt_id: str) -> Any:
        return self._get(f"/api/receipt/{receipt_id}")

    def verdict(self, verdict_id: str) -> Any:
        return self._get(f"/api/verdict/{verdict_id}")
