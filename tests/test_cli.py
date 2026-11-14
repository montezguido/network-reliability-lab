import contextlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from network_reliability.cli import demonstration, main


class CLITests(unittest.TestCase):
    def test_demo_events(self):
        report = demonstration()
        events = [ev["event"] for step in report["timeline"] for ev in step["events"]]
        self.assertEqual(events, ["OPENED", "OPENED", "RECOVERED", "RECOVERED"])

    def test_demo_has_no_network_activity(self):
        with mock.patch("socket.create_connection", side_effect=AssertionError("network used")):
            self.assertEqual(main(["demo"]), 0)

    def test_demo_json_output(self):
        output = StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["demo", "--json"]), 0)
        self.assertEqual(json.loads(output.getvalue())["mode"], "offline-simulation")

    def test_invalid_configuration_returns_2(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "invalid.json"
            config.write_text('{"targets": [{"name": "foo", "protocol": "tcp", '
                              '"host": "8.8.8.8", "port": 53}]}', encoding="utf-8")
            with contextlib.redirect_stderr(StringIO()):
                self.assertEqual(main(["check", "--config", str(config)]), 2)
