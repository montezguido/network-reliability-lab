# Architecture and decisions

```text
[JSON config] -> [Target validation] -> [HTTP/TCP probe] -> [CheckResult]
                                                           |
[Optional JSON state] -> [previous snapshot] -> [transitions] -> [events]
                                                           |
                                                 [JSON/text CLI report]
                                                           |
                                             [atomic snapshot replacement]
```

| Component | Responsibility |
|---|---|
| `models.py` | Validated, immutable target/result/event data models |
| `config.py` | Bounded JSON configuration reader and duplicate-key rejection |
| `checks.py` | Loopback-only, non-redirecting HTTP/TCP probes |
| `incidents.py` | Pure transition logic and snapshot composition |
| `state.py` | Bounded JSON persistence through same-directory temporary replacement |
| `walkthrough.py` | Disposable local HTTP fixture with real 200/503 probe lifecycle |
| `cli.py` | Commands, output and process exit codes |

## Transition rules

- Unknown → `UP`: no incident; unknown → `DOWN`: `OPENED`.
- `UP` → `DOWN`: `OPENED`; `DOWN` → `DOWN`: no additional event.
- `DOWN` → `UP`: `RECOVERED`; `UP` → `UP`: no event.

## Why local-only?

No credentials or uncontrolled scans are needed for reviewer verification. This avoids dependence on cloud infrastructure while remaining a genuine service-checking exercise. The walkthrough uses a real local HTTP server but deliberately simulates HTTP application-level failure (503). The separate manual exercise covers TCP connection failure when the server stops.

## Current tradeoffs

No scheduler, concurrency control or alert destination. Status-only snapshot overwrites previous values; removing configured targets discards their state. HTTP 200 does not prove application readiness. HTTP 503 is treated as `DOWN` by configured expectation, not from business-level diagnostics. These are explicit design constraints.
