# Changelog

All notable changes to the public ACN Preflight package are documented here.

## 0.2.0 - 2026-09-23

### Added

- professional public product documentation and architecture guide;
- Python and MCP integration examples;
- structured client error type;
- environment-based hosted access configuration;
- CLI version and timeout controls;
- CI across supported Python versions;
- CodeQL analysis and Dependabot configuration;
- contribution and security policies;
- GitHub issue and pull-request templates;
- reproducible live contract verification and scheduled public contract checks;
- public trust and verification documentation, support policy, and CODEOWNERS;
- secure PyPI Trusted Publishing through GitHub OIDC;
- package metadata links for the live service, OpenAPI, MCP discovery, trust, and security surfaces;
- package version consistency checks for release metadata;
- five-minute technical evaluator guide for client due diligence.

### Changed

- hardened base URL and timeout validation;
- MCP tools no longer accept access tokens as model-visible parameters;
- package metadata now uses an SPDX Apache-2.0 license declaration;
- Apache-2.0 license file replaced with the canonical full text;
- CLI treats HTTP 402 as an expected structured response while returning nonzero for other HTTP errors;
- CodeQL workflow upgraded to the current v4 major;
- hosted MCP paid authentication moved to transport-level bearer auth, with access tokens removed from model-visible tool schemas;
- Live Contract verification now checks the real hosted MCP tool schema and bearer-auth discovery contract;
- package build gate now runs strict Twine distribution metadata validation.

## 0.1.0 - 2026-09-21

Initial public release with Python client, CLI, MCP server, and hosted ACN Preflight integration.
