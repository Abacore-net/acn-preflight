# Contributing

Thanks for considering a contribution to ACN Preflight.

This repository is the public client and MCP integration layer for a hosted Abacore service. Contributions should preserve that boundary.

## Before opening a pull request

1. Open or identify the issue the change addresses.
2. Keep the public package free of secrets, private evidence, and hosted operational state.
3. Preserve structured response behavior, especially HTTP 402 handling.
4. Add or update tests for behavior changes.
5. Run the local quality checks.

~~~bash
python -m pip install -e ".[dev]"
ruff check src tests examples
python -m unittest discover -s tests -v
python -m build
~~~

## Pull request expectations

A pull request should explain:

- the problem being solved;
- the public behavior that changes;
- security or compatibility implications;
- how the change was tested.

Keep changes focused. Avoid mixing unrelated formatting, dependency, and behavior changes unless they are part of one release-quality objective.

## Security-sensitive changes

Do not put secrets, tokens, wallet material, private endpoints, internal evidence, or deployment credentials in issues, pull requests, fixtures, or examples.

For security findings, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.
