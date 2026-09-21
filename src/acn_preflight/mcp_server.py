from __future__ import annotations

from typing import Any
from mcp.server import MCPServer
from .client import ACNPreflightClient

mcp = MCPServer("ACN Preflight")

def _result(response) -> dict[str, Any]:
    return {"http_status": response.status_code, **response.body}

@mcp.tool()
def bounty_reality_check(issue_url: str) -> dict[str, Any]:
    """Check current public GitHub evidence for a bounty or issue before contributing."""
    return _result(ACNPreflightClient().bounty_reality_check(issue_url))

@mcp.tool()
def repo_contribution_readiness(repo_url: str, change_type: str | None = None, access_token: str | None = None) -> dict[str, Any]:
    """Assess repository contribution readiness. Without paid access this returns the hosted HTTP 402 order payload."""
    return _result(ACNPreflightClient().repo_contribution_readiness(repo_url, change_type=change_type, access_token=access_token))

@mcp.tool()
def payment_preflight(chain: str, address: str, token_contract: str | None = None, amount: str | None = None, access_token: str | None = None) -> dict[str, Any]:
    """Run technical payment preflight. Without paid access this returns the hosted HTTP 402 order payload."""
    return _result(ACNPreflightClient().payment_preflight(chain=chain, address=address, token_contract=token_contract, amount=amount, access_token=access_token))

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
