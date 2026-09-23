# Trust and Verification

ACN Preflight is designed so that important public claims can be checked from machine-readable surfaces instead of relying on screenshots or marketing copy.

## Public evidence surfaces

| Surface | What an integrator can verify |
| --- | --- |
| <code>/health</code> | The public service endpoint is responding |
| <code>/openapi.json</code> | The HTTP contract and capability paths |
| <code>/llms.txt</code> | Agent-readable capability and discovery guidance |
| <code>/.well-known/agent-card.json</code> | Agent identity, provider identity, and supported interface |
| <code>/.well-known/mcp.json</code> | MCP discovery and published tool names |
| <code>/.well-known/x402</code> | Payment metadata and current payment exposure state |
| <code>/agent-readiness.json</code> | External probe evidence and current readiness state |

These surfaces are hosted at https://preflight.abacore.net.

## Fail-closed payment behavior

The payment surface is designed to fail closed.

A paid resource is not supposed to remain published merely because the web server is reachable. The runtime also considers readiness evidence and payment safety state.

When x402 reports <code>SAFETY_HOLD</code>, the manifest must not publish paid resources. This allows an external integrator to distinguish a reachable service from a service that is currently willing to accept paid work.

When x402 reports <code>ACTIVE</code>, the public contract verifier requires a passing readiness proof and the expected paid resource paths.

## Reproduce the verification

Run:

~~~bash
python scripts/verify_live_contract.py
~~~

The verifier uses only the Python standard library and does not require registration, an access token, or payment.

It checks:

1. service health and identity;
2. OpenAPI 3.1 capability paths;
3. llms.txt availability;
4. Agent Card provider identity;
5. MCP tool discovery;
6. readiness proof structure and freshness;
7. Base and USDC x402 identity;
8. consistency between x402 state and published paid resources.

The scheduled GitHub Actions workflow runs the same verifier against the public service.

## What this proves and what it does not

The public verifier proves that the published discovery surfaces are mutually consistent and that the payment publication contract remains fail-closed.

It does not expose private operational evidence, deployment credentials, wallet signing material, internal repositories, or customer data. Those stay behind the hosted service boundary.
