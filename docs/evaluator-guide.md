# Evaluate ACN Preflight in Five Minutes

This guide is for CTOs, engineering leaders, security reviewers, and technical buyers evaluating Abacore's approach to agent-native infrastructure.

The goal is not to ask you to trust a slide deck. The goal is to give you a short path to public, reproducible evidence.

## 1. Confirm the service and machine-readable contract

Open these public endpoints:

- https://preflight.abacore.net/health
- https://preflight.abacore.net/openapi.json
- https://preflight.abacore.net/llms.txt
- https://preflight.abacore.net/.well-known/agent-card.json
- https://preflight.abacore.net/.well-known/mcp.json
- https://preflight.abacore.net/.well-known/x402
- https://preflight.abacore.net/agent-readiness.json

Together they expose service health, the HTTP contract, agent-facing documentation, provider identity, MCP discovery, payment exposure state, and readiness evidence.

## 2. Reproduce the public verification

Clone the repository and run:

~~~bash
python scripts/verify_live_contract.py
~~~

The verifier uses only the Python standard library. It requires no registration, access token, payment, or private infrastructure access.

It checks that the public surfaces agree with one another, including the fail-closed payment invariant.

## 3. Inspect the fail-closed safety behavior

Read:

- [Trust and Verification](trust-and-verification.md)
- [Architecture](architecture.md)

The x402 publication state is not treated as equivalent to “the web server is reachable.”

When the payment surface reports <code>SAFETY_HOLD</code>, paid resources must not be published. When it reports <code>ACTIVE</code>, the verifier requires passing readiness evidence and the expected paid resource paths.

This is a deliberate production pattern: availability alone does not authorize commercial execution.

## 4. Inspect the public integration boundary

The public package supports three integration paths:

- Python;
- CLI;
- MCP.

Review:

- <code>src/acn_preflight/client.py</code>
- <code>src/acn_preflight/cli.py</code>
- <code>src/acn_preflight/mcp_server.py</code>

The MCP tool schema intentionally does not expose hosted access tokens as model-visible arguments. Runtime secrets are injected through the process environment instead.

## 5. Inspect engineering and release controls

The repository exposes its quality controls rather than describing them abstractly:

- CI across supported Python versions;
- package build and strict distribution metadata validation;
- CodeQL analysis;
- scheduled Live Contract verification;
- Dependabot dependency updates;
- CODEOWNERS;
- contribution and security policies;
- PyPI Trusted Publishing workflow using OIDC rather than a long-lived PyPI API token.

Review the workflows under <code>.github/workflows/</code> and the release procedure in [Releasing](releasing.md).

## 6. Try the client

Install directly from the canonical repository:

~~~bash
pip install "git+https://github.com/Abacore-net/acn-preflight"
acn-preflight --version
~~~

Run a public bounty reality check against a GitHub issue you control or are already evaluating:

~~~bash
acn-preflight bounty https://github.com/owner/repo/issues/123
~~~

The client returns structured machine-readable output suitable for automation and agent orchestration.

## 7. What this repository is evidence of

ACN Preflight is deliberately small. It is not intended to expose Abacore's private hosted engine or operational state.

It is intended to make several engineering patterns independently inspectable:

- deterministic gates before external execution;
- machine-readable discovery for agents;
- MCP and HTTP integration surfaces;
- explicit secret boundaries;
- fail-closed commercial exposure;
- reproducible external verification;
- CI and security automation;
- controlled release and supply-chain practices.

For custom agent infrastructure, execution systems, MCP integrations, or other Abacore engineering work, use the contact channel at https://abacore.net.
