# Architecture

ACN Preflight uses a deliberately thin public integration layer in front of a protected hosted decision engine.

## Design objective

The public repository should be inspectable enough that an integrator can understand exactly how a request is formed, how authentication is attached, how errors are represented, and what is returned to the caller.

Commercial logic and sensitive runtime state stay behind the hosted boundary.

## Request path

~~~text
Agent / operator
    |
    +-- MCP
    +-- CLI
    +-- Python
          |
          v
Public acn-preflight package
          |
          | HTTPS + JSON
          v
Hosted ACN Preflight Engine
          |
          v
Fresh public evidence / technical checks
~~~

## Public layer responsibilities

The public package is responsible for:

1. building the documented hosted request;
2. applying an optional bearer token from runtime configuration;
3. enforcing finite network timeouts;
4. preserving HTTP 402 as structured commercial data;
5. rejecting malformed or non-object JSON responses;
6. exposing the same capabilities through Python, CLI, and MCP.

The public package does not make a second hidden decision after the hosted response arrives.

## Hosted boundary

The hosted boundary may contain operational and commercial state that should not be copied into a public SDK. The public repository therefore excludes:

- wallet material and signing secrets;
- payment recipient configuration;
- private evidence;
- deployment controls;
- backup configuration;
- internal safety-gate state;
- private ACN repository history.

## Authentication model

Hosted access can be supplied with <code>ACN_PREFLIGHT_ACCESS_TOKEN</code>.

The MCP tools do not expose a token parameter. This is intentional. A secret should be injected into the MCP process environment by the operator rather than placed in the model-visible tool schema.

The Python client can also receive an explicit token for server-side integrations where the caller already owns secret management.

## Failure model

ACN Preflight distinguishes commercial responses from client failures.

HTTP 402 is returned as a normal <code>ACNResponse</code>. This lets an agent or application inspect the hosted order payload and decide what to do next.

The client raises <code>ACNPreflightError</code> when:

- the hosted endpoint cannot be reached;
- the hosted response is not valid JSON;
- the hosted JSON is not an object.

Configuration errors such as an invalid base URL or non-positive timeout raise <code>ValueError</code> before a network request is attempted.

## Versioning

The package follows semantic versioning while it is in the 0.x line. Public API changes are recorded in <code>CHANGELOG.md</code>.

The hosted engine can evolve independently as long as the public HTTP and response contracts used by this client remain compatible.
