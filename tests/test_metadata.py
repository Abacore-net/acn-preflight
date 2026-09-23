from __future__ import annotations

import re
import unittest
from pathlib import Path

from acn_preflight import __version__
from acn_preflight.client import USER_AGENT

ROOT = Path(__file__).resolve().parents[1]


class MetadataTests(unittest.TestCase):
    def test_package_version_is_consistent(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'^version = "([^"]+)"$', pyproject, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), __version__)
        self.assertEqual(USER_AGENT, f"acn-preflight-python/{__version__}")


if __name__ == "__main__":
    unittest.main()
