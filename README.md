# Network Reliability Lab

**A runnable Python reliability engineering portfolio lab — HTTP/TCP health checks, stateful incident detection, and recovery validation.**

> A self-contained engineering demonstration, not a production monitoring agent. No AWS account, credentials, external destinations, or runtime packages required. This project is separate from private WGU coursework and includes **no WGU solution files**.

## Recruiter / reviewer quick start (two commands)

Requirements: Python 3.11+ from the repository root (on Windows Git Bash, activate your Python virtual environment first).

```bash
python run.py walkthrough
python run_tests.py
```

`walkthrough` launches a temporary HTTP server bound to `127.0.0.1` on an available ephemeral port, makes real HTTP requests, and verifies four states before shutting down the server:

```text
healthy baseline: HTTP 200, UP, events=none
service failure: HTTP 503, DOWN, events=['OPENED']
persistent failure: HTTP 503, DOWN, events=none
recovery: HTTP 200, UP, events=['RECOVERED']
Lifecycle verified
```

*This is the expected illustrative output; run the command to produce a fresh result.* Machine-readable mode: `python run.py walkthrough --json`.

For an entirely network-free demonstration, run `python run.py demo` or `python run.py demo --json`.

## What is implemented?

| Engineering capability | Code location | How to verify |
|---|---|---|
| HTTP/TCP read-only probes and latency measurement | [`checks.py`](src/network_reliability/checks.py) | `test_checks.py` and live walkthrough |
| Strict loopback target validation | [`models.py`](src/network_reliability/models.py) | `test_config.py` |
| Read-once JSON configuration limits | [`config.py`](src/network_reliability/config.py) | `test_config.py` |
| Stateful `OPENED` / `RECOVERED` transitions and repeated-failure suppression | [`incidents.py`](src/network_reliability/incidents.py) | `test_incidents.py`, `test_end_to_end.py` |
| Optional persistent JSON state with atomic replacement | [`state.py`](src/network_reliability/state.py) | `test_state.py`, `test_state_validation.py` |
| CLI, JSON output and meaningful exit codes | [`cli.py`](src/network_reliability/cli.py) | `test_cli.py`, `test_walkthrough.py` |
| Automated cross-platform validation | [GitHub Actions workflow](.github/workflows/test.yml) | Check the **Actions** tab after publication |

**Exit codes:** `0` = healthy/success, `1` = unhealthy service or failed walkthrough, `2` = invalid configuration or local fixture startup error.

## Real outage demonstration (manual exercise)

For a more realistic *connection failure* (not just an HTTP 503), run a disposable local server, stop it, and restart it:

**Terminal A (Git Bash, at the project root):**

```bash
mkdir -p .state/http-root
python -m http.server 8000 --bind 127.0.0.1 --directory .state/http-root
```

**Terminal B (same directory, with Python available):**

```bash
python run.py check --config examples/localhost-http.json --state-file .state/http-lifecycle.json --json
```

Stop Terminal A using **Ctrl+C**, repeat the check twice, then start the server again and check once more. The expected event lifecycle is `[]`, `OPENED`, `[]`, `RECOVERED`. If port 8000 is in use by a different local process, stop that process or choose and configure a different allowed port. The `.state` directory is ignored by Git.

[Documented Windows exercise](docs/evidence/windows-http-lifecycle.md) · [Architecture](docs/architecture.md) · [Security / limitations](docs/security.md) · [Verification report](docs/verification-report.md)

## Design choices and scope

- **Local-first security boundary:** only literal loopback IPs; no DNS names, external host scanning, HTTP redirects, or device remediation.
- **Deterministic incident logic:** pure comparison functions can be tested independently of network adapters.
- **Standard library:** no runtime PyPI dependencies, Docker requirement, or cloud charges.
- **State persistence is optional:** JSON stores only the latest observed statuses; it is **not** an alert history, monitoring database, or locking mechanism.
- **No claims of production capability:** there is no scheduler, external alerting, threshold/hysteresis logic, device management, or hosted deployment.

## Repository validation and status

Run `python -m compileall -q src tests run.py run_tests.py`, `python run_tests.py`, and `python run.py walkthrough --json`. This repository provides executable tests. **A passing GitHub CI badge will only be added after the workflow actually runs successfully.**

The code was developed as a separate portfolio exercise with AI-assisted scaffolding and reviewed through interactive local testing. The maintainer is responsible for understanding, validating, and improving its behavior. This is not a copy of or substitute for restricted WGU assessment solutions.

## Next improvements

Coverage instrumentation, advanced failure classification, safe notifications, durable incident history, static analysis, and more robust multi-process state handling are future work—not features presented as completed.

> **License:** No open-source license has been selected yet. Code is published for review; reuse permission is not implied.
