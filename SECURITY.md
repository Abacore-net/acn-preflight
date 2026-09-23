# Security Policy

## Scope

Security reports are welcome for the public ACN Preflight client, CLI, MCP integration, packaging, and repository automation.

The hosted service is a separate operational boundary. Do not attempt destructive testing, credential guessing, payment abuse, or access to non-public systems.

## Reporting

Do not open a public GitHub issue for a vulnerability.

Report the issue privately through the contact channel published by [Abacore](https://abacore.net). Include:

- the affected version or commit;
- a concise reproduction;
- expected and observed behavior;
- security impact;
- any safe mitigation you have identified.

Do not send access tokens, private keys, seed phrases, or unrelated customer data.

## Secret handling

This repository should never contain hosted access tokens, wallet material, signing secrets, payment-recipient secrets, or private deployment credentials.

The MCP integration intentionally reads hosted access from the process environment rather than exposing secrets as model-visible tool arguments.
