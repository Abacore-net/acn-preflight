from __future__ import annotations

import io
import json
import os
import unittest
import urllib.error
from typing import Any
from unittest.mock import patch

from acn_preflight.client import ACNPreflightClient, ACNPreflightError


class FakeResponse:
    def __init__(self, status: int, body: Any) -> None:
        self.status = status
        self._raw = json.dumps(body).encode()

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *args) -> bool:
        return False


class ClientTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_bounty_builds_get(self, urlopen) -> None:
        urlopen.return_value = FakeResponse(
            200,
            {"capability": "bounty_reality_check"},
        )

        response = ACNPreflightClient(
            "https://example.test"
        ).bounty_reality_check("https://github.com/a/b/issues/1")

        self.assertEqual(response.status_code, 200)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "GET")
        self.assertIn("/v1/bounty?", request.full_url)

    @patch("urllib.request.urlopen")
    def test_paid_402_is_data_not_exception(self, urlopen) -> None:
        body = {
            "error": "payment_required",
            "order_id": "abc",
            "payment_state": "ACTIVE",
        }
        urlopen.side_effect = urllib.error.HTTPError(
            "https://example.test/v1/repo",
            402,
            "Payment Required",
            {},
            io.BytesIO(json.dumps(body).encode()),
        )

        response = ACNPreflightClient(
            "https://example.test"
        ).repo_contribution_readiness(
            "https://github.com/python/cpython",
            change_type="docs",
        )

        self.assertEqual(response.status_code, 402)
        self.assertTrue(response.payment_required)

    @patch("urllib.request.urlopen")
    def test_access_token_is_read_from_environment(self, urlopen) -> None:
        urlopen.return_value = FakeResponse(200, {"ok": True})

        with patch.dict(
            os.environ,
            {"ACN_PREFLIGHT_ACCESS_TOKEN": "secret-token"},
            clear=False,
        ):
            client = ACNPreflightClient("https://example.test")
            client.repo_contribution_readiness("https://github.com/a/b")

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer secret-token",
        )

    @patch("urllib.request.urlopen")
    def test_network_error_is_wrapped(self, urlopen) -> None:
        urlopen.side_effect = urllib.error.URLError("offline")

        client = ACNPreflightClient("https://example.test")
        with self.assertRaises(ACNPreflightError):
            client.x402_manifest()

    @patch("urllib.request.urlopen")
    def test_non_object_json_is_rejected(self, urlopen) -> None:
        urlopen.return_value = FakeResponse(200, ["unexpected"])

        client = ACNPreflightClient("https://example.test")
        with self.assertRaises(ACNPreflightError):
            client.x402_manifest()

    @patch("urllib.request.urlopen")
    def test_x402_manifest_uses_expected_path(self, urlopen) -> None:
        urlopen.return_value = FakeResponse(200, {"version": "1"})

        ACNPreflightClient("https://example.test").x402_manifest()

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://example.test/.well-known/x402",
        )

    def test_invalid_base_url_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ACNPreflightClient("not-a-url")

    def test_base_url_cannot_embed_credentials(self) -> None:
        with self.assertRaises(ValueError):
            ACNPreflightClient("https://user:pass@example.test")

    def test_timeout_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            ACNPreflightClient("https://example.test", timeout=0)


if __name__ == "__main__":
    unittest.main()
