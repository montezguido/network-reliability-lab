# Verification report — v0.2

**Stage:** Public v0.2 release, published and validated by GitHub Actions on 2026-11-14.

## Checks actually performed on this release candidate

Environment: Linux, Python 3.13.5.

| Verification | Observed result |
|---|---|
| `python run_tests.py` | **52 tests passed; 0 skipped; 0 failed** |
| `python -m compileall -q src tests run.py run_tests.py` | Passed |
| `python run.py demo --json` | Offline simulation produces 2 OPENED + 2 RECOVERED events |
| `python run.py walkthrough --json` | Live loopback HTTP: `UP, DOWN, DOWN, UP`; all 4 expected transitions verified |
| Strict input validation and invalid state write tests | Covered by passing local regression tests |
| Build archive CRC validation | Passed |
| Release patch applied to clean v0.1 source tree | Passed; resulting files matched candidate |
| Restricted files/secrets heuristic scan | No actual credential assignments or WGU materials identified; scan has limitations |
| CI workflow configuration | YAML parsed; upstream action commit SHAs verified against GitHub tag refs |
| [GitHub Actions verification](https://github.com/montezguido/network-reliability-lab/actions/runs/43615889906) | **5 of 5 jobs passed** on 2026-11-14: Ubuntu Python 3.11, 3.12, 3.13, 3.14, and Windows Python 3.14 |

## Windows evidence and limitations

The maintainer previously ran **v0.1** in Windows Git Bash using Python 3.14: 43 tests executed, 41 passed, 2 symlink tests skipped. The maintainer also verified the manual UP → DOWN → DOWN → UP service lifecycle with persisted state. See [`docs/evidence/windows-http-lifecycle.md`](evidence/windows-http-lifecycle.md).

Windows v0.2 verification: Tested on Windows using Git Bash and Python 3.14.0. Of 52 tests, 49 passed and 3 symbolic-link tests were skipped because symbolic links were unavailable. Zero failures or errors were reported. The live HTTP walkthrough successfully demonstrated healthy service, outage detection, duplicate-event suppression, and recovery. **GitHub Actions subsequently completed successfully across all five configured Linux/Windows jobs**. The Windows local result and CI matrix are distinct observations.

## Security review scope

Read-only loopback-only network behavior, state validation, error handling, and archive content were reviewed. No third-party runtime dependencies, credentials, privileged device operations, WGU solution files or remote probe targets are included in this release. File read/symlink race conditions, concurrent writer handling, Windows ACL guarantees, and local process tampering are **not solved** by this version. See `docs/security.md`.

This review is neither a pentest nor evidence of production suitability.
