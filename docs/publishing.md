# Publishing to a new GitHub repository (Git Bash)

**Do not begin until the v0.2 patch passes `git apply --check`, the local tests pass, and staged files have been inspected.**

1. Go to https://github.com/new and create an empty **public** repository under `montezguido` named `network-reliability-lab`. **Do not** auto-add a README, license or `.gitignore`; they already exist locally. (Decide on a license before encouraging reuse.)
2. In VS Code Git Bash, open the verified project folder.
3. Initialize Git and check exactly what will be published:

```bash
git init -b main
git add .
git status --short
git diff --cached --stat
git ls-files
```

4. Review the file list and make sure it does not contain `.state/`, `.venv/`, private coursework, passwords, secrets, or unintended files. Stop if any unrecognized file appears.
5. If the staged files are correct, commit and publish:

```bash
git commit -m "feat: publish local network reliability lab"
git remote add origin https://github.com/montezguido/network-reliability-lab.git
git push -u origin main
```

GitHub may ask you to authenticate using your usual browser flow. Never paste a personal access token, password, or recovery code into a chat.

6. Open the repository and inspect the **Code** tab; open **Actions**, verify all matrix jobs, and then pin it to your profile. Do not claim a green workflow until you see it.

If GitHub reports a remote or repository error, inspect with `git remote -v`; do not force-push or delete any repository. Ask for help with the exact error.
