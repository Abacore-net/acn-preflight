from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE_URL = "https://preflight.abacore.net"

@dataclass(frozen=True)
class ACNResponse:
    status_code: int
    body: dict[str, Any]

    @property
    def payment_required(self) -> bool:
        return self.status_code == 402 and self.body.get("error") == "payment_required"

class ACNPreflightClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)

    def _request(self, method: str, path: str, *, payload: dict[str, Any] | None = None, access_token: str | None = None) -> ACNResponse:
        data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
        headers = {"Accept": "application/json", "User-Agent": "acn-preflight-python/0.1.0"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if access_token:
            headers["Authorization"] = "Bearer " + access_token
        req = urllib.request.Request(self.base_url + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read()
                status = int(response.status)
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            status = int(exc.code)
        try:
            body = json.loads(raw.decode("utf-8", "replace"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"ACN returned non-JSON HTTP {status}") from exc
        if not isinstance(body, dict):
            raise RuntimeError(f"ACN returned unexpected JSON HTTP {status}")
        return ACNResponse(status, body)

    def bounty_reality_check(self, issue_url: str) -> ACNResponse:
        query = urllib.parse.urlencode({"issue_url": issue_url})
        return self._request("GET", "/v1/bounty?" + query)

    def repo_contribution_readiness(self, repo_url: str, *, change_type: str | None = None, access_token: str | None = None) -> ACNResponse:
        payload: dict[str, Any] = {"repo_url": repo_url}
        if change_type is not None:
            payload["change_type"] = change_type
        return self._request("POST", "/v1/repo", payload=payload, access_token=access_token)

    def payment_preflight(self, *, chain: str, address: str, token_contract: str | None = None, amount: str | float | None = None, access_token: str | None = None) -> ACNResponse:
        payload: dict[str, Any] = {"chain": chain, "address": address}
        if token_contract is not None:
            payload["token_contract"] = token_contract
        if amount is not None:
            payload["amount"] = amount
        return self._request("POST", "/v1/payment", payload=payload, access_token=access_token)

    def x402_manifest(self) -> ACNResponse:
        return self._request("GET", "/.well-known/x402")
