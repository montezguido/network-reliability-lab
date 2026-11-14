import json
from pathlib import Path
import tempfile
import unittest

from network_reliability.config import load_config, parse_config
from network_reliability.models import ConfigurationError, Target


VALID = {"name": "web_1", "protocol": "http", "host": "127.0.0.1", "port": 8000}


class TargetValidationTests(unittest.TestCase):
    def test_accepts_safe_defaults(self):
        obj = Target.from_dict(VALID)
        self.assertEqual(obj.host, "127.0.0.1")
        self.assertEqual(obj.expected_status, 200)

    def test_accepts_ipv6_loopback(self):
        obj = Target.from_dict({**VALID, "host": "::1"})
        self.assertEqual(obj.host, "::1")

    def test_rejects_remote_targets_and_dns_names(self):
        for host in ["8.8.8.8", "192.168.1.5", "169.254.169.254", "localhost", "example.com"]:
            with self.subTest(host=host), self.assertRaises(ConfigurationError):
                Target.from_dict({**VALID, "host": host})

    def test_rejects_invalid_ports(self):
        for port in [0, -1, 65536, True, 2.3, "8000"]:
            with self.subTest(port=port), self.assertRaises(ConfigurationError):
                Target.from_dict({**VALID, "port": port})

    def test_rejects_bad_paths(self):
        for path in ["http://localhost/", "//evil.com/", "/\r\nX: true", "/?token=abc", "/#fragment", "/x\\y"]:
            with self.subTest(path=path), self.assertRaises(ConfigurationError):
                Target.from_dict({**VALID, "path": path})

    def test_rejects_bad_timeouts(self):
        for timeout in [0, 11, -1, True, "1"]:
            with self.subTest(timeout=timeout), self.assertRaises(ConfigurationError):
                Target.from_dict({**VALID, "timeout_seconds": timeout})

    def test_rejects_unknown_keys(self):
        with self.assertRaises(ConfigurationError):
            Target.from_dict({**VALID, "password": "bad"})

    def test_rejects_tcp_with_http_settings(self):
        with self.assertRaises(ConfigurationError):
            Target.from_dict({**VALID, "protocol": "tcp", "path": "/"})

    def test_rejects_invalid_names(self):
        for name in ["", "../a", "api key", "x" * 61]:
            with self.subTest(name=name), self.assertRaises(ConfigurationError):
                Target.from_dict({**VALID, "name": name})

    def test_rejects_non_ascii_name(self):
        with self.assertRaises(ConfigurationError):
            Target.from_dict({**VALID, "name": "café"})

    def test_rejects_boolean_status(self):
        with self.assertRaises(ConfigurationError):
            Target.from_dict({**VALID, "expected_status": True})


class ConfigurationTests(unittest.TestCase):
    def test_valid_targets(self):
        targets = parse_config({"targets": [VALID]})
        self.assertEqual(len(targets), 1)

    def test_rejects_duplicate_names(self):
        with self.assertRaises(ConfigurationError):
            parse_config({"targets": [VALID, VALID]})

    def test_rejects_extra_top_level_keys(self):
        with self.assertRaises(ConfigurationError):
            parse_config({"targets": [VALID], "debug": True})

    def test_rejects_empty_or_excessive_targets(self):
        for targets in [[], [VALID] * 51]:
            with self.assertRaises(ConfigurationError):
                parse_config({"targets": targets})

    def test_reads_config_from_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            config.write_text(json.dumps({"targets": [VALID]}), encoding="utf-8")
            self.assertEqual(load_config(config)[0].name, "web_1")

    def test_rejects_oversized_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "too-large.json"
            path.write_bytes(b" " * 70000)
            with self.assertRaises(ConfigurationError):
                load_config(path)

    def test_rejects_malformed_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                load_config(path)

    def test_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"targets": [], "targets": []}', encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                load_config(path)

    def test_rejects_configuration_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "actual.json"
            source.write_text(json.dumps({"targets": [VALID]}), encoding="utf-8")
            link = Path(directory) / "alias.json"
            try:
                link.symlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable on this system")
            with self.assertRaises(ConfigurationError):
                load_config(link)
