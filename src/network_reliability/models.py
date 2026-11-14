"""Validated models for a deliberately restricted network health-check lab."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import ipaddress
import re
from typing import Any


class ConfigurationError(ValueError):
    """Raised for unsafe or malformed user-supplied configuration."""


@dataclass(frozen=True, slots=True)
class Target:
    name: str
    protocol: str
    host: str
    port: int
    path: str = "/"
    expected_status: int = 200
    timeout_seconds: float = 2.0

    @classmethod
    def from_dict(cls, raw: Any) -> "Target":
        if not isinstance(raw, dict):
            raise ConfigurationError("Each target must be an object")
        allowed = {
            "name", "protocol", "host", "port", "path", "expected_status", "timeout_seconds"
        }
        unknown = set(raw) - allowed
        if unknown:
            raise ConfigurationError(f"Unknown target settings: {', '.join(sorted(unknown))}")
        for key in ("name", "protocol", "host", "port"):
            if key not in raw:
                raise ConfigurationError(f"Missing required setting: {key}")
        name = raw["name"]
        if not isinstance(name, str) or not (1 <= len(name) <= 60):
            raise ConfigurationError("Target name must be 1 to 60 characters")
        if re.fullmatch(r"[A-Za-z0-9_-]{1,60}", name) is None:
            raise ConfigurationError("Target names may contain only letters, numbers, - and _")
        protocol = raw["protocol"]
        if protocol not in ("tcp", "http"):
            raise ConfigurationError("Protocol must be 'tcp' or 'http'")
        host = raw["host"]
        if not isinstance(host, str):
            raise ConfigurationError("Host must be an IP literal")
        try:
            address = ipaddress.ip_address(host)
        except ValueError as exc:
            raise ConfigurationError("Host must be a literal loopback IP address") from exc
        if not address.is_loopback:
            raise ConfigurationError("Only loopback IP addresses are allowed in this lab")
        port = raw["port"]
        if type(port) is not int or not (1 <= port <= 65535):
            raise ConfigurationError("Port must be an integer between 1 and 65535")
        path = raw.get("path", "/")
        if (not isinstance(path, str) or not path.startswith("/") or
                path.startswith("//") or len(path) > 256 or
                any(ord(char) < 32 or ord(char) == 127 for char in path) or
                "#" in path or "?" in path or "\\" in path):
            raise ConfigurationError("Path must be a safe, simple absolute path")
        status = raw.get("expected_status", 200)
        if type(status) is not int or not (100 <= status <= 599):
            raise ConfigurationError("expected_status must be an HTTP status from 100 to 599")
        timeout = raw.get("timeout_seconds", 2.0)
        if type(timeout) not in (int, float) or not (0.1 <= timeout <= 10.0):
            raise ConfigurationError("timeout_seconds must be between 0.1 and 10")
        if protocol == "tcp" and ("path" in raw or "expected_status" in raw):
            raise ConfigurationError("TCP checks cannot specify HTTP-only settings")
        return cls(name, protocol, str(address), port, path, status, float(timeout))


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    status: str
    protocol: str
    latency_ms: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class IncidentEvent:
    target: str
    event: str
    previous: str | None
    current: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
