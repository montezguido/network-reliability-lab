import json
import os
from pathlib import Path
import tempfile
import unittest

from network_reliability.models import ConfigurationError
from network_reliability.state import read_state, write_state


class StateTests(unittest.TestCase):
    def test_missing_file_is_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(read_state(Path(folder) / "missing.json"), {})

    def test_writes_reads_and_replaces(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "state.json"
            write_state(p, {"web": "UP"})
            self.assertEqual(read_state(p), {"web": "UP"})
            write_state(p, {"web": "DOWN"})
            self.assertEqual(read_state(p), {"web": "DOWN"})
            self.assertEqual(list(Path(folder).iterdir()), [p])
            if os.name == "posix":
                self.assertEqual(p.stat().st_mode & 0o777, 0o600)

    def test_invalid_state_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "bad.json"
            for contents in ['{"a": "BROKEN"}', "[]", "invalid"]:
                p.write_text(contents, encoding="utf-8")
                with self.assertRaises(ConfigurationError):
                    read_state(p)

    def test_duplicate_state_keys_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "duplicate.json"
            p.write_text('{"web": "DOWN", "web": "UP"}', encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                read_state(p)

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "target.json"
            target.write_text(json.dumps({"web": "UP"}), encoding="utf-8")
            link = Path(folder) / "alias.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable on this system")
            with self.assertRaises(ConfigurationError):
                read_state(link)
            with self.assertRaises(ConfigurationError):
                write_state(link, {"web": "DOWN"})
            self.assertEqual(json.loads(target.read_text()), {"web": "UP"})

    def test_missing_parent_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ConfigurationError):
                write_state(Path(folder) / "absent" / "state.json", {"web": "UP"})
