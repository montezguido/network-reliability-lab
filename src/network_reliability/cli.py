"""Command-line entry point for a safe, inspectable reliability demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .checks import perform_check
from .config import load_config
from .incidents import current_snapshot, transitions
from .models import CheckResult, ConfigurationError
from .state import read_state, write_state
from .walkthrough import live_http_walkthrough


def demonstration() -> dict:
    """Deterministic, fully offline incident lifecycle; no connections are made."""
    scenarios = [
        ("baseline", {"web": "UP", "api": "UP"}),
        ("web outage", {"web": "DOWN", "api": "UP"}),
        ("api outage", {"web": "DOWN", "api": "DOWN"}),
        ("recovery", {"web": "UP", "api": "UP"}),
    ]
    previous: dict[str, str] = {}
    timeline = []
    for label, statuses in scenarios:
        results = [CheckResult(name, status, "simulated", 0.0, "synthetic demo")
                   for name, status in statuses.items()]
        events = transitions(previous, results)
        timeline.append({"step": label, "statuses": statuses,
                         "events": [event.to_dict() for event in events]})
        previous = current_snapshot(results)
    return {"mode": "offline-simulation", "timeline": timeline}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nr-lab", description="Local-only health monitoring and offline incident simulation"
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    demo = subcommands.add_parser("demo", help="Demonstrate incidents without any networking")
    demo.add_argument("--json", action="store_true", help="Output JSON instead of a text summary")
    walkthrough = subcommands.add_parser("walkthrough", help="Run real loopback HTTP lifecycle evidence")
    walkthrough.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    check = subcommands.add_parser("check", help="Probe only explicitly configured loopback IPs")
    check.add_argument("--config", required=True, type=Path)
    check.add_argument("--state-file", type=Path, help="Optional persistent incident state")
    check.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        report = demonstration()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            for entry in report["timeline"]:
                print(f"{entry['step']}: {entry['statuses']}")
                for event in entry["events"]:
                    print(f"  {event['event']}: {event['target']}")
        return 0
    if args.command == "walkthrough":
        try:
            report = live_http_walkthrough()
        except OSError:
            print("Unable to start the local HTTP fixture", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            for entry in report["timeline"]:
                events = [event["event"] for event in entry["events"]]
                print(f"{entry['step']}: HTTP {entry['fixture_http_status']}, "
                      f"{entry['result']['status']}, events={events or 'none'}")
            print("Lifecycle verified" if report["verified"] else "Lifecycle failed")
        return 0 if report["verified"] else 1
    try:
        targets = load_config(args.config)
        previous = read_state(args.state_file) if args.state_file else {}
        results = [perform_check(target) for target in targets]
        events = transitions(previous, results)
        if args.state_file:
            write_state(args.state_file, current_snapshot(results))
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    report = {"mode": "local-loopback", "results": [result.to_dict() for result in results],
              "events": [event.to_dict() for event in events]}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for result in results:
            print(f"{result.name}: {result.status} ({result.reason}, {result.latency_ms} ms)")
        for event in events:
            print(f"{event.event}: {event.target}")
    return 1 if any(result.status == "DOWN" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
