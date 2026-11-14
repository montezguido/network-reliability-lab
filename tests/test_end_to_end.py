"""Integration test of the CLI across real local service outage and recovery."""

import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
import json
from pathlib import Path
import tempfile
import threading
import unittest

from network_reliability.cli import main


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


class IncidentLifecycleIntegrationTest(unittest.TestCase):
    def test_outage_and_recovery(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            config = base / "targets.json"
            state = base / "state.json"
            config.write_text(json.dumps({"targets": [{"name": "web", "protocol": "http",
                "host": "127.0.0.1", "port": port}]}), encoding="utf-8")

            def check():
                out = StringIO()
                with contextlib.redirect_stdout(out):
                    exit_code = main(["check", "--config", str(config),
                                     "--state-file", str(state), "--json"])
                return exit_code, json.loads(out.getvalue())

            try:
                code, first = check()
                self.assertEqual(code, 0)
                self.assertEqual(first["results"][0]["status"], "UP")
                self.assertEqual(first["events"], [])
                server.shutdown()
                thread.join(timeout=3)
                server.server_close()
                code, second = check()
                self.assertEqual(code, 1)
                self.assertEqual(second["results"][0]["status"], "DOWN")
                self.assertEqual(second["events"][0]["event"], "OPENED")

                recovered = ThreadingHTTPServer(("127.0.0.1", port), Handler)
                recovered_thread = threading.Thread(target=recovered.serve_forever, daemon=True)
                recovered_thread.start()
                try:
                    code, third = check()
                    self.assertEqual(code, 0)
                    self.assertEqual(third["results"][0]["status"], "UP")
                    self.assertEqual(third["events"][0]["event"], "RECOVERED")
                finally:
                    recovered.shutdown()
                    recovered.server_close()
                    recovered_thread.join(timeout=3)
            finally:
                # Close safely even when an assertion fails before the outage.
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
