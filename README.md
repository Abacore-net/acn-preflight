# ACN Preflight

[![CI](https://github.com/Abacore-net/acn-preflight/actions/workflows/ci.yml/badge.svg)](https://github.com/Abacore-net/acn-preflight/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Abacore-net/acn-preflight/actions/workflows/codeql.yml/badge.svg)](https://github.com/Abacore-net/acn-preflight/actions/workflows/codeql.yml)
[![Live Contract](https://github.com/Abacore-net/acn-preflight/actions/workflows/live-contract.yml/badge.svg)](https://github.com/Abacore-net/acn-preflight/actions/workflows/live-contract.yml)

Deterministic preflight checks for AI agents before they spend time, money, or execution effort on external work.

ACN Preflight is the public integration layer for the hosted Abacore Preflight Engine. It exposes the same decision surfaces through Python, CLI, and Model Context Protocol (MCP), while keeping payment configuration, wallet material, deployment controls, and private operational evidence outside the public repository.

## Evaluate Abacore in five minutes

If you are evaluating Abacore for agent infrastructure, machine-to-machine integrations, or production AI execution, start with the [5-minute technical evaluator guide](docs/evaluator-guide.md).

It walks through the live public contract, reproducible verification, fail-closed behavior, SDK boundaries, CI/security controls, and release discipline using evidence you can inspect yourself. The public checks require no account, token, payment, or private access.

## Live proof

The hosted engine publishes machine-readable discovery and trust surfaces that can be inspected without registration or payment.

| Public surface | Purpose |
| --- | --- |
| [Health](https://preflight.abacore.net/health) | Minimal public availability check |
| [OpenAPI 3.1](https://preflight.abacore.net/openapi.json) | HTTP capability contract |
| [llms.txt](https://preflight.abacore.net/llms.txt) | Agent-readable capability guidance |
| [Agent Card](https://preflight.abacore.net/.well-known/agent-card.json) | Agent and provider identity |
| [MCP discovery](https://preflight.abacore.net/.well-known/mcp.json) | Published MCP tools |
| [x402 manifest](https://preflight.abacore.net/.well-known/x402) | Payment metadata and exposure state |
| [Readiness proof](https://preflight.abacore.net/agent-readiness.json) | External probe evidence and readiness state |

Reproduce the public verification locally:

~~~bash
python scripts/verify_live_contract.py
~~~

The verifier also checks the fail-closed invariant: if x402 reports <code>SAFETY_HOLD</code>, paid resources must not be published. See [Trust and Verification](docs/trust-and-verification.md) for the verification model and its boundaries.

## What it checks

| Capability | Question answered | Public entry point |
| --- | --- | --- |
| Bounty reality check | Is a public GitHub issue or bounty still worth pursuing based on current evidence? | <code>bounty_reality_check</code> |
| Repository contribution readiness | Is a repository ready for a specific type of contribution before an agent starts work? | <code>repo_contribution_readiness</code> |
| Payment preflight | Is a Base payment surface technically ready before a payment attempt? | <code>payment_preflight</code> |

The hosted service returns machine-readable JSON. Paid capabilities return HTTP 402 with the hosted order payload until valid hosted access is configured.

## Why this exists

Autonomous and semi-autonomous agents can waste significant effort when they act before validating the target environment. ACN Preflight moves that validation into a small, deterministic gate that can be called before contribution, payment, or other external execution.

The public client is intentionally thin:

- no LLM is used in the client answer path;
- no wallet or payment-recipient material is stored here;
- no private ACN operational history is published here;
- hosted responses are returned without hidden client-side reinterpretation;
- the same capability contract is available to humans, scripts, and agents.

## Quick start

Python 3.10 or newer is required.

Until the package is published on PyPI, install from the canonical GitHub repository:

~~~bash
pip install "git+https://github.com/Abacore-net/acn-preflight"
~~~

Verify the installation:

~~~bash
acn-preflight --version
acn-preflight --help
~~~

Run a public bounty check:

~~~bash
acn-preflight bounty https://github.com/owner/repo/issues/123
~~~

Check repository readiness:

~~~bash
acn-preflight repo https://github.com/python/cpython --change-type docs
~~~

Inspect the hosted x402 manifest:

~~~bash
acn-preflight x402
~~~

## Python

~~~python
from acn_preflight import ACNPreflightClient

client = ACNPreflightClient()

response = client.bounty_reality_check(
    "https://github.com/owner/repo/issues/123"
)

print(response.status_code)
print(response.body)
~~~

For hosted paid access, configure the token as an environment variable rather than placing it in source code, command history, or an MCP tool argument:

~~~bash
export ACN_PREFLIGHT_ACCESS_TOKEN="your-hosted-access-token"
~~~

The client also supports:

- <code>ACN_PREFLIGHT_BASE_URL</code> for controlled endpoint overrides;
- <code>ACN_PREFLIGHT_ACCESS_TOKEN</code> for hosted access;
- an explicit timeout in Python or with CLI <code>--timeout</code>.

## MCP

Start the stdio MCP server:

~~~bash
uvx --from "git+https://github.com/Abacore-net/acn-preflight" acn-preflight-mcp
~~~

A generic MCP client configuration is included in <code>examples/mcp_config.json</code>:

~~~json
{
  "mcpServers": {
    "acn-preflight": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Abacore-net/acn-preflight",
        "acn-preflight-mcp"
      ]
    }
  }
}
~~~

The MCP tools deliberately do not accept access tokens as model-visible parameters. If paid access is required, provide <code>ACN_PREFLIGHT_ACCESS_TOKEN</code> to the MCP process environment.

## Public architecture

~~~mermaid
flowchart LR
    A[AI agent or operator] --> B[MCP]
    A --> C[CLI]
    A --> D[Python client]
    B --> E[Public ACN Preflight integration layer]
    C --> E
    D --> E
    E -->|HTTPS and structured JSON| F[Hosted ACN Preflight Engine]
    F --> G[Fresh public evidence and technical checks]
~~~

The repository contains the transport and integration contract. The protected hosted engine remains the execution boundary for commercial logic and private operational state.

See [Architecture](docs/architecture.md) for the trust boundary and failure model.

## Response behavior

The Python client returns an <code>ACNResponse</code> with:

- <code>status_code</code>, the HTTP status returned by the hosted service;
- <code>body</code>, the hosted JSON object without hidden rewriting;
- <code>payment_required</code>, a convenience property for a hosted HTTP 402 payment-required response.

The CLI emits a stable JSON envelope containing <code>http_status</code> and <code>body</code>.

HTTP 402 is treated as a valid commercial response, not as a client exception. Network failures, invalid endpoints, and malformed hosted responses fail explicitly.

## Security boundary

This repository intentionally excludes:

- payment recipient configuration;
- wallet material and signing secrets;
- hosted access tokens;
- safety-gate state;
- backup and deployment configuration;
- private evidence and internal ACN repository history.

Secrets should be supplied through the runtime environment. See [SECURITY.md](SECURITY.md) before reporting a vulnerability.

## Development

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check src tests examples
python -m unittest discover -s tests -v
python -m build
~~~

Pull requests run linting, unit tests across supported Python versions, package build checks, and CodeQL analysis.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution expectations, [SUPPORT.md](SUPPORT.md) for support channels, [CHANGELOG.md](CHANGELOG.md) for release notes, and [Releasing](docs/releasing.md) for the Trusted Publishing release path.

## What this repository demonstrates

ACN Preflight is intentionally compact. The public repository is designed to demonstrate an Abacore pattern that is useful for production agent systems: keep the client surface simple and inspectable, keep secrets and commercial state behind a controlled boundary, expose deterministic machine-readable contracts, and make the integration usable through standard developer and agent interfaces.

Built by [Abacore](https://abacore.net).

## License

Apache-2.0. See [LICENSE](LICENSE).
