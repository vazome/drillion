# Security

## Threat model

drillion runs arbitrary Python on your machine, by design, and only on your machine.

- **Task code and your own code are not sandboxed.** A submission is graded by running it
  in a pytest subprocess (`src/drillion/runner.py`) with the same interpreter and the same
  permissions as the app. A 10-second per-test timeout and a 60-second wall cap stop a
  runaway loop; nothing stops a program that decides to read or write your files.
- **The server is local and single-user.** It binds `127.0.0.1`, and `TrustedHostMiddleware`
  refuses any host but `127.0.0.1` and `localhost` (`src/drillion/api.py`). There is no
  hosted or multi-user mode, no accounts, and none is planned. Do not expose the port.
- **A task folder is code, not data.** `task.py` executes on import, so a contributed task
  is reviewed the way a pull request is reviewed — as code.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/vazome/drillion/security/advisories/new).
Please do not open a public issue for something exploitable.
