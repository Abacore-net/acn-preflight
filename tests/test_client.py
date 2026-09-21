from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch
import urllib.error
from acn_preflight.client import ACNPreflightClient

class FakeResponse:
    def __init__(self, status: int, body: dict) -> None:
        self.status = status
        self._raw = json.dumps(body).encode()
    def read(self): return self._raw
    def __enter__(self): return self
    def __exit__(self, *args): return False

class ClientTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_bounty_builds_get(self, urlopen):
        urlopen.return_value = FakeResponse(200, {"capability": "bounty_reality_check"})
        response = ACNPreflightClient("https://example.test").bounty_reality_check("https://github.com/a/b/issues/1")
        self.assertEqual(response.status_code, 200)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "GET")
        self.assertIn("/v1/bounty?", request.full_url)

    @patch("urllib.request.urlopen")
    def test_paid_402_is_data_not_exception(self, urlopen):
        body = {"error": "payment_required", "order_id": "abc", "payment_state": "ACTIVE"}
        urlopen.side_effect = urllib.error.HTTPError("https://example.test/v1/repo", 402, "Payment Required", {}, io.BytesIO(json.dumps(body).encode()))
        response = ACNPreflightClient("https://example.test").repo_contribution_readiness("https://github.com/python/cpython", change_type="docs")
        self.assertEqual(response.status_code, 402)
        self.assertTrue(response.payment_required)

if __name__ == "__main__":
    unittest.main()
