"""Tests for the reviewer-facing real HTTP lifecycle command."""

import contextlib
from io import StringIO
import json
import unittest

from network_reliability.cli import main
from network_reliability.walkthrough import live_http_walkthrough


class WalkthroughTests(unittest.TestCase):
    def test_real_http_lifecycle(self):
        report = live_http_walkthrough()
        self.assertTrue(report["verified"])
        self.assertEqual([step["result"]["status"] for step in report["timeline"]],
                         ["UP", "DOWN", "DOWN", "UP"])
        self.assertEqual([[item["event"] for item in step["events"]]
                          for step in report["timeline"]],
                         [[], ["OPENED"], [], ["RECOVERED"]])
        self.assertEqual([step["fixture_http_status"] for step in report["timeline"]],
                         [200, 503, 503, 200])

    def test_cli_walkthrough_json(self):
        output = StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["walkthrough", "--json"]), 0)
        self.assertTrue(json.loads(output.getvalue())["verified"])
