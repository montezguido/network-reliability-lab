# Windows local HTTP lifecycle — observed exercise

**Evidence type:** User-reported terminal output from the local Windows Git Bash exercise, November 2026. These figures were supplied during interactive testing; they are **not** results of a CI workflow and no screenshot is included here.

Environment: Windows, Git Bash, Python 3.14 in `.venv`; target `127.0.0.1:8000`; local `http.server` bound to loopback only. Command:

```bash
python run.py check --config examples/localhost-http.json --state-file .state/http-lifecycle.json --json
```

| Observation | Result | Probe duration | Event |
|---|---|---:|---|
| Healthy baseline with server running | `UP`, `HTTP 200` | 64.77 ms | None |
| Server stopped with Ctrl+C | `DOWN`, `TimeoutError` | 1017.81 ms | `OPENED`, previous `UP` |
| Repeated check while server remained unavailable | `DOWN`, `TimeoutError` | 1007.68 ms | No duplicate event |
| Server restarted | `UP`, `HTTP 200` | 11.72 ms | `RECOVERED`, previous `DOWN` |
| State file checked after recovery | `{ "demo_web": "UP" }` | — | Last status persisted |

**Interpretation:** The exercises validate the current status, event transitions and last-status persistence for this local fixture. Timeouts alone do not establish the cause of an outage outside this deliberately controlled exercise.

**Reproduce:** Follow the two-terminal procedure in the [README](../../README.md#real-outage-demonstration-manual-exercise). Timing varies by computer; state and events are the key acceptance criteria.
