"""Regression tests ensuring invalid state is rejected before filesystem writes."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from network_reliability.models import ConfigurationError
from network_reliability.state import read_state, validate_state, write_state


class StateValidationTests(unittest.TestCase):
    def test_write_rejects_invalid_data_without_creating_file(self):
        invalid = [
            {"web": "UNKNOWN"}, {"": "UP"}, {"../bad": "UP"},
            {"name with spaces": "DOWN"}, {"web": True},
            {"a" * 61: "UP"}, {f"t{i}": "UP" for i in range(51)},
            ["UP"],
        ]
        with tempfile.TemporaryDirectory() as folder:
            for value in invalid:
                with self.subTest(value=str(value)[:70]):
                    file = Path(folder) / "state.json"
                    with self.assertRaises(ConfigurationError):
                        write_state(file, value)
                    self.assertFalse(file.exists())
                    self.assertEqual(list(Path(folder).iterdir()), [])

    def test_write_rejects_invalid_data_without_overwriting_good_state(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "state.json"
            write_state(file, {"web": "UP"})
            original = file.read_bytes()
            with self.assertRaises(ConfigurationError):
                write_state(file, {"web": "ERROR"})
            self.assertEqual(file.read_bytes(), original)

    def test_read_rejects_invalid_target_names(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "state.json"
            for name in ["../outside", "", "service name", "⚡"]:
                file.write_text(json.dumps({name: "UP"}), encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(ConfigurationError):
                    read_state(file)

    def test_failed_replacement_leaves_original_unchanged_and_no_temp_files(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "state.json"
            write_state(file, {"web": "UP"})
            with mock.patch("network_reliability.state.os.replace", side_effect=PermissionError):
                with self.assertRaises(ConfigurationError):
                    write_state(file, {"web": "DOWN"})
            self.assertEqual(read_state(file), {"web": "UP"})
            self.assertEqual(list(Path(folder).iterdir()), [file])

    def test_symlink_parent_rejected_when_supported(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "actual"
            destination.mkdir()
            shortcut = Path(folder) / "link"
            try:
                shortcut.symlink_to(destination, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable on this system")
            with self.assertRaises(ConfigurationError):
                write_state(shortcut / "state.json", {"web": "UP"})

    def test_empty_state_is_valid(self):
        self.assertEqual(validate_state({}), {})
