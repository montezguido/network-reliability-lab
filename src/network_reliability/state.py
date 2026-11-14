"""Optional local JSON state snapshots; trusted local directory required.

Replacement is atomic on supported local filesystems. POSIX mode 0600 is used
for the temporary file; Windows permissions depend on the directory ACL.
Concurrent writers and adversarial filesystem changes are not supported.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

from .config import _reject_duplicate_keys
from .models import ConfigurationError

MAX_STATE_BYTES = 16_384
MAX_STATES = 50


def validate_state(value: Any) -> dict[str, str]:
    """Validate the complete snapshot before either accepting or writing it."""
    if not isinstance(value, dict) or len(value) > MAX_STATES:
        raise ConfigurationError("State must be an object with at most 50 targets")
    for name, status in value.items():
        if not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,60}", name) is None:
            raise ConfigurationError("State contains an invalid target name")
        if type(status) is not str or status not in ("UP", "DOWN"):
            raise ConfigurationError("State contains an invalid target status")
    return value


def read_state(path: Path) -> dict[str, str]:
    if path.is_symlink():
        raise ConfigurationError("Refusing a symbolic-link state file")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_STATE_BYTES + 1)
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise ConfigurationError("Unable to read state file") from exc
    if len(raw) > MAX_STATE_BYTES:
        raise ConfigurationError("State file exceeds the size limit")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigurationError("State file contains invalid UTF-8 JSON") from exc
    return validate_state(data)


def write_state(path: Path, states: dict[str, str]) -> None:
    validate_state(states)  # Fail before creating or replacing any file.
    if path.is_symlink():
        raise ConfigurationError("Refusing a symbolic-link state file")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise ConfigurationError("State file needs a real existing parent directory")
    payload = json.dumps(states, sort_keys=True, indent=2) + "\n"
    if len(payload.encode("utf-8")) > MAX_STATE_BYTES:
        raise ConfigurationError("State is too large")
    fd, temporary = tempfile.mkstemp(prefix=".nr-state-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name == "posix":
            os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    except OSError as exc:
        raise ConfigurationError("Unable to write state file") from exc
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
