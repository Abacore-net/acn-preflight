from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from unittest.mock import patch

from acn_preflight import ACNResponse
from acn_preflight.cli import main


class CLITests(unittest.TestCase):
    @patch("acn_preflight.cli.ACNPreflightClient")
    def test_bounty_command_emits_stable_json(self, client_class) -> None:
        client_class.return_value.bounty_reality_check.return_value = ACNResponse(
            200,
            {"capability": "bounty_reality_check"},
        )

        stdout = io.StringIO()
        argv = [
            "acn-preflight",
            "bounty",
            "https://github.com/a/b/issues/1",
        ]

        with (
            patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(stdout),
            self.assertRaises(SystemExit) as exit_context,
        ):
            main()

        self.assertEqual(exit_context.exception.code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["http_status"], 200)
        self.assertEqual(
            payload["body"]["capability"],
            "bounty_reality_check",
        )

    @patch("acn_preflight.cli.ACNPreflightClient")
    def test_http_402_is_successful_cli_flow(self, client_class) -> None:
        client_class.return_value.repo_contribution_readiness.return_value = ACNResponse(
            402,
            {"error": "payment_required"},
        )

        stdout = io.StringIO()
        argv = [
            "acn-preflight",
            "repo",
            "https://github.com/a/b",
        ]

        with (
            patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(stdout),
            self.assertRaises(SystemExit) as exit_context,
        ):
            main()

        self.assertEqual(exit_context.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
