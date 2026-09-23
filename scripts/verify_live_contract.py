from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://preflight.abacore.net"
EXPECTED_PAID_PATHS = {"/v1/repo", "/v1/payment"}
EXPECTED_MCP_TOOLS = {
    "bounty_reality_check",
    "repo_contribution_readiness",
    "payment_preflight",
}


class VerificationError(RuntimeError):
    pass


def _request(base_url: str, path: str, *, timeout: float) -> tuple[int, str, str]:
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "acn-preflight-live-verifier/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            return (
                int(response.status),
                response.headers.get("content-type", ""),
                raw.decode("utf-8", "replace"),
            )
    except urllib.error.URLError as exc:
        raise VerificationError(f"{path}: request failed: {exc}") from exc


def _post_json(
    base_url: str,
    path: str,
    payload: dict[str, Any],
    *,
    timeout: float,
) -> dict[str, Any]:
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "User-Agent": "acn-preflight-live-verifier/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if int(response.status) != 200:
                raise VerificationError(f"{path}: expected HTTP 200, got {response.status}")
            raw = response.read().decode("utf-8", "replace")
    except urllib.error.URLError as exc:
        raise VerificationError(f"{path}: request failed: {exc}") from exc
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{path}: response is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise VerificationError(f"{path}: expected a JSON object")
    return parsed


def _json(base_url: str, path: str, *, timeout: float) -> dict[str, Any]:
    status, _, body = _request(base_url, path, timeout=timeout)
    if status != 200:
        raise VerificationError(f"{path}: expected HTTP 200, got {status}")
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{path}: response is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise VerificationError(f"{path}: expected a JSON object")
    return parsed


def _checked_age_seconds(value: str) -> float:
    try:
        checked = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise VerificationError("agent-readiness.json: invalid checked_at timestamp") from exc
    if checked.tzinfo is None:
        raise VerificationError("agent-readiness.json: checked_at must be timezone-aware")
    return (dt.datetime.now(dt.timezone.utc) - checked).total_seconds()


def verify(base_url: str, timeout: float) -> dict[str, Any]:
    status, _, health = _request(base_url, "/health", timeout=timeout)
    if status != 200 or health.strip() != "ok":
        raise VerificationError("/health: expected HTTP 200 with body 'ok'")

    root = _json(base_url, "/", timeout=timeout)
    if root.get("service") != "ACN Preflight Engine":
        raise VerificationError("/: unexpected service identity")

    openapi = _json(base_url, "/openapi.json", timeout=timeout)
    if not str(openapi.get("openapi", "")).startswith("3.1"):
        raise VerificationError("/openapi.json: expected OpenAPI 3.1")
    paths = set((openapi.get("paths") or {}).keys())
    required_paths = {"/v1/bounty", *EXPECTED_PAID_PATHS}
    if not required_paths.issubset(paths):
        raise VerificationError("/openapi.json: required capability paths are missing")

    status, _, llms = _request(base_url, "/llms.txt", timeout=timeout)
    if status != 200 or "ACN Preflight Engine" not in llms:
        raise VerificationError("/llms.txt: public agent documentation is unavailable")

    agent_card = _json(base_url, "/.well-known/agent-card.json", timeout=timeout)
    provider = agent_card.get("provider") or {}
    if agent_card.get("name") != "ACN Preflight" or provider.get("organization") != "Abacore":
        raise VerificationError("agent-card.json: unexpected service or provider identity")

    mcp = _json(base_url, "/.well-known/mcp.json", timeout=timeout)
    if not EXPECTED_MCP_TOOLS.issubset(set(mcp.get("tools") or [])):
        raise VerificationError("mcp.json: expected MCP tools are missing")
    authentication = mcp.get("authentication") or {}
    if authentication.get("scheme") != "bearer":
        raise VerificationError("mcp.json: paid MCP authentication must use bearer transport auth")

    remote_tools = _post_json(
        base_url,
        "/mcp",
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        timeout=timeout,
    )
    tool_rows = ((remote_tools.get("result") or {}).get("tools") or [])
    tools_by_name = {
        row.get("name"): row
        for row in tool_rows
        if isinstance(row, dict) and isinstance(row.get("name"), str)
    }
    if not EXPECTED_MCP_TOOLS.issubset(tools_by_name):
        raise VerificationError("/mcp tools/list: expected tools are missing")
    for name in ("repo_contribution_readiness", "payment_preflight"):
        schema = (tools_by_name[name].get("inputSchema") or {})
        required = set(schema.get("required") or [])
        properties = set((schema.get("properties") or {}).keys())
        if "access_token" in required or "access_token" in properties:
            raise VerificationError(
                f"/mcp tools/list: {name} exposes access_token to the model-visible schema"
            )

    readiness = _json(base_url, "/agent-readiness.json", timeout=timeout)
    if readiness.get("status") not in {"PASS", "FAIL"}:
        raise VerificationError("agent-readiness.json: unexpected status")
    if readiness.get("probe_type") != "dual_external_provider":
        raise VerificationError("agent-readiness.json: dual external proof is missing")
    if readiness.get("network_loopback") is not False:
        raise VerificationError("agent-readiness.json: network_loopback must be false")

    age = _checked_age_seconds(str(readiness.get("checked_at") or ""))
    if age < -60:
        raise VerificationError("agent-readiness.json: checked_at is unexpectedly in the future")
    if age > 86400:
        raise VerificationError("agent-readiness.json: proof is older than 24 hours")

    x402 = _json(base_url, "/.well-known/x402", timeout=timeout)
    if x402.get("network") != "Base" or x402.get("chain_id") != 8453:
        raise VerificationError("x402: unexpected network identity")
    if x402.get("asset") != "USDC":
        raise VerificationError("x402: unexpected settlement asset")

    payment_state = x402.get("payment_state")
    resource_rows = x402.get("resources") or []
    resources = {
        row if isinstance(row, str) else row.get("path")
        for row in resource_rows
        if isinstance(row, (str, dict))
    }
    resources.discard(None)
    if payment_state == "ACTIVE":
        if readiness.get("status") != "PASS":
            raise VerificationError("x402: ACTIVE requires a PASS readiness proof")
        if not EXPECTED_PAID_PATHS.issubset(resources):
            raise VerificationError("x402: ACTIVE state is missing paid resources")
    elif payment_state == "SAFETY_HOLD":
        if resources:
            raise VerificationError("x402: SAFETY_HOLD must not publish paid resources")
    else:
        raise VerificationError(f"x402: unexpected payment_state {payment_state!r}")

    return {
        "status": "PASS",
        "base_url": base_url.rstrip("/"),
        "service": root.get("service"),
        "openapi": openapi.get("openapi"),
        "mcp_tools": sorted(EXPECTED_MCP_TOOLS),
        "mcp_secret_schema_invariant": "PASS",
        "readiness_status": readiness.get("status"),
        "readiness_age_seconds": round(age, 1),
        "x402_payment_state": payment_state,
        "paid_resources_published": sorted(resources),
        "fail_closed_invariant": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the public ACN Preflight discovery and safety contract.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    try:
        result = verify(args.base_url, args.timeout)
    except (VerificationError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error": str(exc),
                },
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
