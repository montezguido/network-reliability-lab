"""Read-only TCP and HTTP checks. No DNS resolution, redirects, or remote targets."""

from __future__ import annotations

import http.client
import socket
import time

from .models import CheckResult, Target


def perform_check(target: Target) -> CheckResult:
    """Probe a previously validated loopback target once and close the connection."""
    started = time.perf_counter()
    status = "DOWN"
    reason = "unexpected result"
    try:
        if target.protocol == "tcp":
            with socket.create_connection((target.host, target.port), target.timeout_seconds):
                status, reason = "UP", "TCP connection established"
        else:
            connection = http.client.HTTPConnection(
                target.host, port=target.port, timeout=target.timeout_seconds
            )
            try:
                connection.request("GET", target.path, headers={"Connection": "close"})
                response = connection.getresponse()
                if response.status == target.expected_status:
                    status, reason = "UP", f"HTTP {response.status}"
                else:
                    status, reason = "DOWN", f"HTTP {response.status} (expected {target.expected_status})"
            finally:
                connection.close()
    except (OSError, http.client.HTTPException) as exc:
        # Don't emit exception internals or user-controlled payloads into logs.
        reason = f"Probe failed ({type(exc).__name__})"
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return CheckResult(target.name, status, target.protocol, elapsed_ms, reason)
