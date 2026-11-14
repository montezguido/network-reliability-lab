"""Strict JSON configuration loading with small, well-defined inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ConfigurationError, Target

MAX_CONFIG_BYTES = 65_536
MAX_TARGETS = 50


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise ConfigurationError(f"Duplicate JSON field: {name}")
        result[name] = value
    return result


def parse_config(document: Any) -> list[Target]:
    if not isinstance(document, dict) or set(document) != {"targets"}:
        raise ConfigurationError("Configuration must contain only a 'targets' array")
    raw_targets = document["targets"]
    if not isinstance(raw_targets, list) or not 1 <= len(raw_targets) <= MAX_TARGETS:
        raise ConfigurationError(f"targets must contain between 1 and {MAX_TARGETS} objects")
    targets = [Target.from_dict(item) for item in raw_targets]
    names = [target.name for target in targets]
    if len(names) != len(set(names)):
        raise ConfigurationError("Target names must be unique")
    return targets


def load_config(path: Path) -> list[Target]:
    if path.is_symlink():
        raise ConfigurationError("Refusing configuration from a symbolic link")
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_CONFIG_BYTES + 1)
    except OSError as exc:
        raise ConfigurationError("Cannot read configuration file") from exc
    if len(data) > MAX_CONFIG_BYTES:
        raise ConfigurationError("Configuration is larger than the size limit")
    try:
        decoded = json.loads(data.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigurationError("Configuration must contain valid UTF-8 JSON") from exc
    return parse_config(decoded)
