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
- GitHub issue and pull-request templates.

### Changed

- hardened base URL and timeout validation;
- MCP tools no longer accept access tokens as model-visible parameters;
- package metadata now uses an SPDX Apache-2.0 license declaration;
- Apache-2.0 license file replaced with the canonical full text;
- CLI treats HTTP 402 as an expected structured response while returning nonzero for other HTTP errors.

## 0.1.0 - 2026-09-21

Initial public release with Python client, CLI, MCP server, and hosted ACN Preflight integration.
