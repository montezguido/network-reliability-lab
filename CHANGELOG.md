# Changelog

## v0.2.0 — Portfolio review candidate

- Added a one-command live HTTP walkthrough (`python run.py walkthrough`) using a temporary loopback-only fixture.
- Added state validation **before** writing to prevent invalid snapshots from replacing good data.
- Aligned target/state identifiers with a simple ASCII identifier policy.
- Expanded regression tests for state integrity and the reviewer walkthrough.
- Updated CI to include Linux Python 3.11–3.14 and Windows Python 3.14; pinned current upstream action commits.
- Revised the recruiter-facing README and security limitations.

## v0.1.0 — Initial local lab

- Offline incident demo, loopback-only HTTP/TCP probes, JSON state, tests, CI template.
