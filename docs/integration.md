# Integration Guide

This guide covers the three public integration surfaces: Python, CLI, and MCP.

## Environment

The default hosted endpoint is:

~~~text
https://preflight.abacore.net
~~~

Supported environment variables:

| Variable | Purpose |
| --- | --- |
| <code>ACN_PREFLIGHT_BASE_URL</code> | Override the hosted endpoint for a controlled environment |
| <code>ACN_PREFLIGHT_ACCESS_TOKEN</code> | Provide hosted paid access without placing a secret in code or tool arguments |

## Python

~~~python
from acn_preflight import ACNPreflightClient

client = ACNPreflightClient(timeout=20)

bounty = client.bounty_reality_check(
    "https://github.com/owner/repo/issues/123"
)

repo = client.repo_contribution_readiness(
    "https://github.com/python/cpython",
    change_type="docs",
)

payment = client.payment_preflight(
    chain="base",
    address="0xYOUR_WALLET_ADDRESS",
)

manifest = client.x402_manifest()
~~~

Each call returns an <code>ACNResponse</code>.

## CLI

~~~bash
acn-preflight bounty https://github.com/owner/repo/issues/123
acn-preflight repo https://github.com/python/cpython --change-type docs
acn-preflight payment --chain base --address 0xYOUR_WALLET_ADDRESS
acn-preflight x402
~~~

The CLI writes a JSON object to stdout. Configuration or transport errors are written as structured JSON to stderr and return exit code 1.

HTTP 402 remains a successful CLI transport flow and returns exit code 0 because it is an expected hosted commercial response.

## MCP

Start the server:

~~~bash
acn-preflight-mcp
~~~

Or run directly from GitHub with uvx:

~~~bash
uvx --from "git+https://github.com/Abacore-net/acn-preflight" acn-preflight-mcp
~~~

Available tools:

- <code>bounty_reality_check</code>
- <code>repo_contribution_readiness</code>
- <code>payment_preflight</code>

The MCP tool schema contains no access-token field. Configure paid hosted access in the process environment.

## Production recommendations

- pin a reviewed package or commit version;
- set an explicit timeout appropriate to the calling workflow;
- keep the default HTTPS endpoint unless you control the alternate environment;
- inject tokens from a secret manager or process environment;
- log response status and high-level outcome, but do not log tokens;
- treat malformed hosted responses as a hard integration failure.
