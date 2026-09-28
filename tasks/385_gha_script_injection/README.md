---
title: "script injection: an issue title that runs as code"
difficulty: medium
minutes: 15
prereqs: [377]
track: github-actions
tags: [security, expressions]
kind: workflow
edits: .github/workflows/triage.yml
---
# script injection: an issue title that runs as code

*Anyone can open an issue, and its title is whatever they typed. A workflow that writes the title into a shell script lets them write the script.*

## Read first
- [Security hardening: understanding the risk of script injections](https://docs.github.com/en/actions/concepts/security/script-injections): the attack, and the fix
- [actionlint: untrusted inputs](https://github.com/rhysd/actionlint/blob/main/docs/checks.md#untrusted-inputs): which contexts it treats as attacker-controlled

## Why
An expression in a workflow is not a variable. GitHub evaluates it and pastes the result into the text of the step **before** the shell ever sees it. For a value the repository controls, a branch name it created or a version it chose, that is harmless. For a value an outsider controls, an issue title, a pull request's body, a commit message, a branch name from a fork, it means they are editing the script: a double quote closes the string, a semicolon starts their command, and it runs with the job's token.

The fix is one move. Give the value to the step through `env`, where it becomes an environment variable, and use it in the script as `"$TITLE"`, quoted. The shell reads a variable's value as data and never parses it as code, whatever it contains. The issue number is a number and cannot carry a command, but it goes through `env` too, so the script holds no expression at all and a reviewer can see that at a glance.

actionlint knows which contexts outsiders control, and refuses `github.event.issue.title` inside `run`: the vulnerable workflow does not pass its check.

## You get
An empty `.github/workflows/triage.yml`, and beside it `SECURITY-REPORT.md`, read-only: the report of how the current version is exploited, with its code. Whatever you type is linted by actionlint when you run it, offline. Nothing is run.

## You return
The fixed `triage` workflow: the same trigger, token and behaviour as the reported one, with every value from the issue reaching the script through `env`.

## Rules
- `name: triage`, `on.issues.types` is exactly `[opened]`, and the workflow's `permissions` is exactly `issues: write`
- exactly one job, `triage`, on `ubuntu-latest`, with exactly one step
- the step's `run` is exactly two lines, `echo "New issue: $TITLE"` and `gh issue edit "$NUMBER" --add-label triage`, and holds no `${{{{` expression
- the step's `env` is exactly `GH_TOKEN: ${{{{ github.token }}}}`, `GH_REPO: ${{{{ github.repository }}}}`, `TITLE: ${{{{ github.event.issue.title }}}}` and `NUMBER: ${{{{ github.event.issue.number }}}}`

## Hints
### Hint 1
The attack in the report works because the title is pasted into the script. Where could it go instead, so the script only ever names it?

### Hint 2
`env` on a step turns expressions into environment variables for that step:

```yaml
        env:
          TITLE: ${{ github.event.issue.title }}
          NUMBER: ${{ github.event.issue.number }}
```

### Hint 3
The script names the variables, in double quotes, and nothing else:

```yaml
      - run: |
          echo "New issue: $TITLE"
          gh issue edit "$NUMBER" --add-label triage
```
