# Reproducible verification

From the repository root:

```bash
python -m compileall -q src tests run.py run_tests.py
python run_tests.py
python run.py demo --json
python run.py walkthrough --json
```

`walkthrough` opens one ephemeral loopback HTTP port and closes it before exiting. No cloud access, credentials or persistent file changes are required.

For a manually stopped server and persistent JSON state, follow the [README](../README.md#real-outage-demonstration-manual-exercise).

After pushing, open the GitHub Actions tab and confirm the OS/Python matrix result, including any Windows symlink skips. Do not put a green CI badge in README until GitHub actually runs.
