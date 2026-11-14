"""One-command, real loopback HTTP lifecycle demonstration for reviewers.

Uses an in-process ephemeral-port HTTP server: no cloud credentials, remote
hosts, privileged ports, state file, or permanent background service.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from typing import Any

from .checks import perform_check
from .incidents import current_snapshot, transitions
from .models import Target


class _FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        # A fixed path prevents accidental exposure of local application files.
        status = self.server.response_status if self.path == "/health" else 404
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass


def live_http_walkthrough() -> dict[str, Any]:
    """Check real HTTP 200/503 responses and their state transitions."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FixtureHandler)
    server.response_status = 200
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    previous: dict[str, str] = {}
    timeline: list[dict[str, Any]] = []
    # Same service, four observations: UP, first DOWN, repeated DOWN, recovered UP.
    scenarios = [
        ("healthy baseline", 200, "UP", []),
        ("service failure", 503, "DOWN", ["OPENED"]),
        ("persistent failure", 503, "DOWN", []),
        ("recovery", 200, "UP", ["RECOVERED"]),
    ]
    verified = True
    target = Target.from_dict({"name": "demo_web", "protocol": "http",
                               "host": "127.0.0.1", "port": server.server_port,
                               "path": "/health", "expected_status": 200,
                               "timeout_seconds": 2.0})
    try:
        for label, response_status, expected_status, expected_events in scenarios:
            server.response_status = response_status
            result = perform_check(target)
            events = transitions(previous, [result])
            observed_events = [event.event for event in events]
            step_ok = result.status == expected_status and observed_events == expected_events
            verified = verified and step_ok
            timeline.append({
                "step": label,
                "fixture_http_status": response_status,
                "result": result.to_dict(),
                "events": [event.to_dict() for event in events],
                "verified": step_ok,
            })
            previous = current_snapshot([result])
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=3)
    return {"mode": "live-loopback-walkthrough", "verified": verified, "timeline": timeline}
