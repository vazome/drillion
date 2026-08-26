---
title: mocking — patch where it is used, then read the calls
difficulty: medium
tier: packages
track: rsample
minutes: 20
prereqs: []
tags: [testing]
---
# mocking — patch where it is used, then read the calls

*Tests that hit the real webhook are slow, flaky, and occasionally page a colleague.*

## Why
The deploy script has a step that posts an alert to the company chat when a deploy finishes. You need to test that step in CI, but a test that really posts to chat is slow, needs real credentials, and spams colleagues on every test run. Instead you temporarily swap the real "send" function for a stand-in that just records what it was asked to send, run the code, read the recording, and put the real function back. Both functions live at the bottom of this file; you write the test.

## You get
`version` — a string like `"v2.1.0"`.

`host` — a string like `"hooks.internal:443"`.

The test creates both. The real `send_alert` in this file raises an error if it is ever truly called, which is how the test proves you swapped it out.

## You return
a dict with four keys: `"result"` (what `run_deploy` returned), `"calls"` (how many times the stand-in was called), `"url"` (the first argument it received) and `"payload"` (the second argument). The real `send_alert` must be back in place by the time you return.

## Rules
Test `run_deploy` without letting `send_alert` touch the network.

Two functions live at the bottom of this file. `send_alert` is the real call — it raises `RuntimeError` if it ever actually runs. `run_deploy` is the code under test: it builds a URL and a payload, hands them to `send_alert`, and folds the reply into its own return value. Read both before starting.

Do this:

1. Replace `send_alert` with a `Mock`, in the module where `run_deploy` looks the name up.
2. Make that `Mock` return `{"status": "ok"}` when it is called.
3. Call `run_deploy(version, host)` and keep what it returns.
4. Return a dict with exactly these keys:

   ```text
   {"result": <what run_deploy returned>,
    "calls": <how many times the mock was called>,
    "url": <the first argument it was called with>,
    "payload": <the second argument>}
   ```

5. Undo the patch before you return. Use `with patch(...)` or the decorator — not a bare assignment over the name, which leaks into every test that runs after yours. The test checks that the real `send_alert` is back.

```python
solve("v2.1.0", "hooks.internal:443")
# -> {"result": "v2.1.0 ok",
#     "calls": 1,
#     "url": "https://hooks.internal:443/hooks/deploy",
#     "payload": {"version": "v2.1.0", "status": "done"}}
```

> [!WARNING]
> The rule people get wrong: patch the name in the module that USES it, not the module that defines it. If `run_deploy` had done `from alerts import send_alert`, then this module owns its own reference called `send_alert`, and patching `"alerts.send_alert"` changes a name nobody looks at any more. Here both live in one file. This module is `sys.modules[__name__]`, so `patch.object(sys.modules[__name__], "send_alert")` is how you spell that target — the dotted-string form `patch("pkg.send_alert")` cannot name a module whose folder starts with a digit.

Constraint: no imports beyond `unittest.mock` and `sys` (`sys` is already imported for you at the top of the file).

## Read first
- [Understanding the Python mock object library](https://realpython.com/python-mock-library/) — swapping a real function for a fake inside a test
- [unittest.mock.patch](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch) — the swap that puts the original back for you, plus `patch.object`

> [!NOTE]
> **Take-home:** `monkeypatch.setattr(...)`

## Hints
### Hint 1
A Mock is a stand-in that answers any attribute you ask for and records every call it receives. patch swaps one in for a real name for the length of a block and puts the original back afterwards. The part worth slowing down over is which name gets swapped: the one the code under test resolves at call time, which is not always where the function was written.
### Hint 2
from unittest.mock import patch, then `with patch.object(MODULE, 'send_alert') as fake:` where MODULE is the module the code under test looks the name up in — inside this file that is `sys.modules[__name__]`. Set fake.return_value before calling run_deploy, since run_deploy reads a key off the reply. Afterwards fake.call_count and fake.call_args carry the recording; call_args.args is the tuple of positional arguments.
### Hint 3
Different data — patching a clock that another module imported:

```python
# app.py:  from time import time      <- app now owns a name 'time'
#          def stamp():
#              return f'at {time()}'
from unittest.mock import patch
with patch('app.time') as fake:       # app.time, NOT time.time
    fake.return_value = 100.0
    print(stamp())           # at 100.0
    print(fake.call_count)   # 1
    print(fake.call_args)    # call()
print(stamp())               # at 1786... the real clock is back
```

Same three beats as yours: swap the name the caller uses, configure the return, read the recording.
