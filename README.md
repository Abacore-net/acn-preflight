# ACN Preflight

Python client and MCP server for the hosted ACN Preflight Engine at https://preflight.abacore.net.

One engine exposes three tools:

- `bounty_reality_check`: fresh public GitHub issue reality check.
- `repo_contribution_readiness`: repository contribution-readiness preflight.
- `payment_preflight`: Base payment-surface technical preflight.

The paid tools return the hosted service's HTTP 402 response and order payload until a valid access token is supplied.

## Install

```bash
pip install acn-preflight
uvx --from acn-preflight acn-preflight --help
uvx --from acn-preflight acn-preflight-mcp
```

## CLI

```bash
acn-preflight bounty https://github.com/owner/repo/issues/123
acn-preflight repo https://github.com/python/cpython --change-type docs
acn-preflight payment --chain base --address 0xYOUR_WALLET_ADDRESS
acn-preflight x402
```

## MCP

Run `acn-preflight-mcp` to expose all three capabilities from one stdio MCP server.

## Security boundary

This repository contains only the public client and MCP integration layer. It intentionally excludes payment recipient configuration, wallet material, safety-gate state, backup configuration, deployment guards, private evidence, and private ACN repository history.

## License

Apache-2.0.
