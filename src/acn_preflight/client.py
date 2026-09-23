from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_BASE_URL = "https://preflight.abacore.net"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "acn-preflight-python/0.2.0"


class ACNPreflightError(RuntimeError):
    """Raised when the public client cannot obtain a valid hosted response."""


@dataclass(frozen=True)
class ACNResponse:
    status_code: int
    body: dict[str, Any]

    @property
    def payment_required(self) -> bool:
        return self.status_code == 402 and self.body.get("error") == "payment_required"


class ACNPreflightClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        access_token: str | None = None,
    ) -> None:
        configured_base_url = base_url or os.getenv(
            "ACN_PREFLIGHT_BASE_URL",
            DEFAULT_BASE_URL,
        )
        self.base_url = self._normalize_base_url(configured_base_url)

        self.timeout = float(timeout)
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        self.access_token = access_token or os.getenv("ACN_PREFLIGHT_ACCESS_TOKEN") or None

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        value = base_url.strip()
        parsed = urllib.parse.urlsplit(value)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must be an absolute http or https URL")
        if parsed.username or parsed.password:
            raise ValueError("base_url must not contain embedded credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain a query string or fragment")

        return value.rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        access_token: str | None = None,
    ) -> ACNResponse:
        data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
        headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if data is not None:
            headers["Content-Type"] = "application/json"

        token = access_token if access_token is not None else self.access_token
        if token:
            headers["Authorization"] = "Bearer " + token

        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers=headers,
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                status = int(response.status)
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            status = int(exc.code)
        except urllib.error.URLError as exc:
            raise ACNPreflightError(
                f"Could not reach ACN Preflight at {self.base_url}: {exc.reason}"
            ) from exc

        try:
            body = json.loads(raw.decode("utf-8", "replace"))
        except json.JSONDecodeError as exc:
            raise ACNPreflightError(f"ACN returned non-JSON HTTP {status}") from exc

        if not isinstance(body, dict):
            raise ACNPreflightError(f"ACN returned unexpected JSON HTTP {status}")

        return ACNResponse(status_code=status, body=body)

    def bounty_reality_check(self, issue_url: str) -> ACNResponse:
        query = urllib.parse.urlencode({"issue_url": issue_url})
        return self._request("GET", "/v1/bounty?" + query)

    def repo_contribution_readiness(
        self,
        repo_url: str,
        *,
        change_type: str | None = None,
        access_token: str | None = None,
    ) -> ACNResponse:
        payload: dict[str, Any] = {"repo_url": repo_url}
        if change_type is not None:
            payload["change_type"] = change_type
        return self._request(
            "POST",
            "/v1/repo",
            payload=payload,
            access_token=access_token,
        )

    def payment_preflight(
        self,
        *,
        chain: str,
        address: str,
        token_contract: str | None = None,
        amount: str | float | None = None,
        access_token: str | None = None,
    ) -> ACNResponse:
        payload: dict[str, Any] = {
            "chain": chain,
            "address": address,
        }
        if token_contract is not None:
            payload["token_contract"] = token_contract
        if amount is not None:
            payload["amount"] = amount
        return self._request(
            "POST",
            "/v1/payment",
            payload=payload,
            access_token=access_token,
        )

    def x402_manifest(self) -> ACNResponse:
        return self._request("GET", "/.well-known/x402")
