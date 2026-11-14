"""Deterministic incident transitions, decoupled from any ticketing provider."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import CheckResult, IncidentEvent


def transitions(previous: Mapping[str, str], results: Iterable[CheckResult]) -> list[IncidentEvent]:
    events: list[IncidentEvent] = []
    for result in results:
        before = previous.get(result.name)
        after = result.status
        if after not in ("UP", "DOWN"):
            raise ValueError("Only UP/DOWN result states are supported")
        if before is not None and before not in ("UP", "DOWN"):
            raise ValueError("Invalid previous state")
        if before == after or (before is None and after == "UP"):
            continue
        event = "OPENED" if after == "DOWN" else "RECOVERED"
        events.append(IncidentEvent(result.name, event, before, after))
    return events


def current_snapshot(results: Iterable[CheckResult]) -> dict[str, str]:
    return {result.name: result.status for result in results}
