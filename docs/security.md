# Security model (v0.2)

## Intended usage

A **single-user, trusted-local-computer** learning application. It is **not** hardened for untrusted directories, concurrent writers, multi-user hosts or production networks.

## Defenses actually implemented

- CLI configuration only permits literal loopback IPv4/IPv6 addresses and strict port/timeouts; no hostnames or remote network destinations.
- HTTP checks are read-only GETs; no redirects, cookies, authentication, or external data are transmitted.
- JSON configuration and state have byte-size limits, duplicate-key rejection and validated shapes/statuses.
- Both configuration and state reject symbolic-link final paths when detectable. This does **not** eliminate path race conditions in adversarial shared filesystems.
- State updates use a temporary file and `os.replace`, reducing partial-write risk; failures are surfaced without overwriting the prior snapshot. This does **not** prevent concurrent processes overwriting each other's snapshots.
- Temporary state files are owner-only on POSIX via mode `0600`; **Windows access is governed by inherited directory ACLs**, not equivalent Unix mode protection.
- No third-party runtime dependencies, shell execution, Telnet, SSH, or embedded secrets.

## What is not guaranteed

- Port availability. Loopback HTTP tests may fail if restricted by local firewall settings or other services.
- Protection from another local process tampering with trusted file paths or racing between `is_symlink` and `open`.
- Cross-process transaction semantics, state history, data encryption, file ACL management or permission preservation across filesystems.
- Security for user-provided `--state-file` paths outside trusted local project directories.
- Production SRE features, service authentication, external notifications or real-world remediation.

## Before making the repository public

1. Review tracked **and staged** content for credentials, private addresses, WGU materials, tokens, metadata, and unexpected binaries. Do not rely on `.gitignore` to clean old commits.
2. Keep private coursework **outside** this Git repository; never commit original WGU ZIPs or copies of assessment solution files.
3. Leave `.venv`, `.state`, logs, local JSON overrides and secrets out of Git history.
4. Confirm CI only runs reviewed local checks, uses minimal `GITHUB_TOKEN` rights and pinned actions.
5. Enable GitHub account MFA and secret scanning/branch protections when available.
6. Validate the GitHub Actions runs before adding any badge or claiming CI has passed.

A clean heuristic secret scan is not an independent penetration test or a guarantee of zero vulnerabilities.
