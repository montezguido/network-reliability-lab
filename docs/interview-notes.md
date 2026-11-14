# Technical explanation practice

**Problem:** Reliability teams need a way to distinguish one failed check from an ongoing incident and a later recovery.

**Design:** I created an independently implemented Python CLI with validated configuration, TCP/HTTP probes, a pure state-transition layer, optional persisted state, and automated tests. It is deliberately local-only so reviewers can run it without cloud bills or production access.

**Safety:** All live probes are restricted to loopback IP literals. Inputs and timeouts are validated; no credentials, remote remediation, Telnet, or shell commands are involved.

**Verification:** I can demonstrate a healthy local web server, stop it, show a failed probe/incident opening, restart it, and show recovery. Unit tests validate malformed configuration and transition behavior.

**Tradeoffs:** No concurrency, rate-limits, external alerting, or historical metrics yet. It is an educational demonstrator rather than a production monitoring platform.

**Interview prompt to practice:** Why did you separate incident transition logic from the networking layer? Answer: so we can test critical behavior deterministically without live network dependencies, and replace adapters independently.
