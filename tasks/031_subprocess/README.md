---
title: subprocess.run — run a command, read the result
difficulty: easy
tier: core
minutes: 15
prereqs: []
tags: [stdlib-ops]
---
# subprocess.run — run a command, read the result

*Every deploy script shells out; subprocess.run is how Python does it safely.*

## Read first
- [subprocess](https://devdocs.io/python~3.14/library/subprocess) — `run`, `capture_output=True`, `text=True`, and `.returncode`
- [subprocess security](https://devdocs.io/python~3.14/library/subprocess#security-considerations) — why `shell=True` is the wrong default

## Why
A deploy script has to run other command-line tools (kubectl, terraform, a health check) and decide what to do based on whether each one succeeded and what it printed. The team lead wants one helper that runs a command and reports back in one tidy package: did it succeed, the exit code, its normal output and its error output. It must never glue the command into one string, because that is how attackers sneak extra commands in.

## You get
`argv` — a list of strings: the program name followed by its arguments, like `["echo", "hi"]`. The test creates it and hands it to you; you never build it yourself. The examples below say `echo` because it reads well; the test itself always runs a Python child process, which behaves the same on every platform.

## You return
a dict with exactly the keys `"ok"`, `"code"`, `"out"` and `"err"`, as described in the rules below.

## Rules
Run the command `argv` (a list like `["echo", "hi"]`) and report on it. Return a dict with exactly these keys:

```python
solve(["echo", "hi"])
# -> {"ok": True,     # returncode == 0
#     "code": 0,      # the returncode itself
#     "out": "hi",    # stdout, stripped of surrounding whitespace
#     "err": ""}      # stderr, stripped the same way

solve(["false"])
# -> {"ok": False, "code": 1, "out": "", "err": ""}
```

- Pass `argv` straight to `subprocess.run` as a LIST. Never join it into a string with `shell=True` — that is how injection bugs happen, and the list form does not need it.
- Capture both streams as text, not bytes.
- A non-zero exit must NOT raise. Either skip `check=True`, or use it and catch `subprocess.CalledProcessError`. Both give the same dict here.

## Hints
### Hint 1
subprocess.run returns a CompletedProcess object. Everything you need — return code, stdout, stderr — is an attribute on it. By default though, output goes to the terminal instead of being captured, and it arrives as bytes. Two keyword arguments fix that.
### Hint 2
The keywords are capture_output=True and text=True. Then read .returncode, .stdout and .stderr off the result. check=True would raise CalledProcessError on non-zero exit — here you want the code either way, so plain run without check is the shorter route.
### Hint 3
Different command, same moves:

```python
import subprocess, sys
res = subprocess.run([sys.executable, '--version'],
                     capture_output=True, text=True)
print(res.returncode)        # 0
print(res.stdout.strip())    # Python 3.12.x
```

Build your dict from those three attributes.
