import http.server
import socket
import threading
import unittest

from network_reliability.checks import perform_check
from network_reliability.models import Target


class QuietHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        code = 302 if self.path == "/redirect" else 200
        self.send_response(code)
        if code == 302:
            self.send_header("Location", "http://example.com/")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass


class ProbeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def target(self, protocol="http", path="/", expected_status=200):
        return Target("web", protocol, "127.0.0.1", self.server.server_port,
                      path, expected_status, 1.0)

    def test_http_healthy(self):
        checked = perform_check(self.target())
        self.assertEqual(checked.status, "UP")
        self.assertEqual(checked.reason, "HTTP 200")

    def test_http_mismatch_is_down(self):
        checked = perform_check(self.target(expected_status=204))
        self.assertEqual(checked.status, "DOWN")
        self.assertIn("HTTP 200", checked.reason)

    def test_http_redirect_is_not_followed(self):
        checked = perform_check(self.target(path="/redirect"))
        self.assertEqual(checked.status, "DOWN")
        self.assertIn("HTTP 302", checked.reason)

    def test_tcp_healthy(self):
        self.assertEqual(perform_check(self.target(protocol="tcp")).status, "UP")

    def test_tcp_unavailable(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            free_port = listener.getsockname()[1]
        target = Target("missing", "tcp", "127.0.0.1", free_port, timeout_seconds=0.2)
        self.assertEqual(perform_check(target).status, "DOWN")

    def test_latency_is_nonnegative(self):
        self.assertGreaterEqual(perform_check(self.target()).latency_ms, 0)
