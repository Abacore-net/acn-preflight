# Releasing ACN Preflight

ACN Preflight releases are designed to use GitHub Releases plus PyPI Trusted Publishing. No long-lived PyPI API token is required.

## Release prerequisites

The GitHub repository must have an environment named <code>pypi</code>. PyPI must trust the GitHub Actions publisher for this repository and workflow.

Trusted Publisher identity:

| Field | Value |
| --- | --- |
| PyPI project | <code>acn-preflight</code> |
| GitHub owner | <code>Abacore-net</code> |
| Repository | <code>acn-preflight</code> |
| Workflow | <code>publish.yml</code> |
| Environment | <code>pypi</code> |

If the PyPI project does not exist yet, configure a pending Trusted Publisher. The first successful publication creates the project.

## Release sequence

1. Update the package version in <code>pyproject.toml</code> and <code>src/acn_preflight/__init__.py</code>.
2. Update <code>CHANGELOG.md</code>.
3. Merge the release pull request only after CI, CodeQL, and Live Contract checks pass.
4. Create a GitHub Release whose tag matches the package version, for example <code>v0.2.0</code>.
5. Publish the GitHub Release.
6. GitHub Actions builds the sdist and wheel, validates them with Twine, and publishes them to PyPI using OIDC.
7. Verify the package page and install the exact released version in a clean environment.

~~~bash
python -m venv /tmp/acn-preflight-release-check
source /tmp/acn-preflight-release-check/bin/activate
python -m pip install "acn-preflight==0.2.0"
acn-preflight --version
~~~

## Security properties

The publishing job receives only <code>id-token: write</code>. It does not store a PyPI username, password, or API token in repository secrets.

Protect the <code>pypi</code> GitHub environment with required reviewers before using the release workflow. This adds a human release gate after all automated validation has passed.
