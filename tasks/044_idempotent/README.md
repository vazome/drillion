---
title: idempotency — apply desired state, safe to re-run
difficulty: medium
tier: core
minutes: 15
prereqs: [4, 36]
tags: [errors]
---
# idempotency — apply desired state, safe to re-run

*Ops scripts get re-run — after a crash, by a retry, by a nervous human at 3am.*

## Why
A service's settings (replica count, image version, debug flag) are applied by a script. That script gets run again and again: after a crash, by an automatic retry, by a colleague at 3am who is not sure it ran. Running it twice must not break anything, and it must only report changes that really happened, so the team can tell genuine drift from noise in the audit log. Your job: compare what is with what should be, change only what differs, and list exactly what you touched.

## You get
`state` — a dict of the settings as they are right now, like `{"replicas": "2", "debug": "on"}`.

`desired` — a dict of how the settings should be, like `{"replicas": "3", "debug": None}`; a value of `None` means "this setting must not exist".

The test creates both and hands them to you.

## You return
a pair (tuple) of two things: a new dict with the corrected settings, and a sorted list of short strings saying what you did, like `["remove debug", "update replicas"]`. Running your function again on its own output must give the same settings and an empty list.

## Rules
Bring `state` in line with `desired` and report what you changed.

`state` is the resource as it is right now: a dict of key → value. `desired` is how it should look: key → wanted value, where the value `None` means "this key must not be present".

Return the tuple `(new_state, changes)`:

- `new_state`: a NEW dict. Do not mutate the one you were handed.
- `changes`: a sorted list of strings, one per key you actually touched, each formatted `"<action> <key>"` where action is `add`, `update` or `remove`.

For each key in `desired`:

| Case | What you do | What you record |
| --- | --- | --- |
| want is `None`, key is in `state` | drop it | `"remove <key>"` |
| want is `None`, key is absent | nothing | — |
| key is not in `state` | set it | `"add <key>"` |
| key is in `state`, value differs | set it | `"update <key>"` |
| key is in `state`, value already equal | nothing | — |

Keys in `state` that `desired` never mentions are left alone — you only manage what you were asked to manage.

```python
state   = {"replicas": "2", "image": "api:1.4", "debug": "on"}
desired = {"replicas": "3", "image": "api:1.4", "debug": None}
solve(state, desired)
# -> ({"replicas": "3", "image": "api:1.4"},
#     ["remove debug", "update replicas"])
```

Feed `new_state` back in with the same `desired` and you must get an identical state and an empty changes list. That is what idempotent means, and it is exactly what the test does: run once, then run again on the result.

## Hints
### Hint 1
The whole task is the comparison before the write. Code that just assigns every desired key produces the right state but reports a change every single run, so nobody can tell a real drift from noise. Second trap: writing into the dict you were given means the caller's 'before' is gone and you can no longer diff against it.
### Hint 2
Start with new = dict(state) and changes = []. Loop over desired.items(). Three tests in order: want is None, then key not in new, then new[key] != want. Removal is del new[key] or new.pop(key). Return (new, sorted(changes)) so the order never depends on dict order.
### Hint 3
Different data — reconciling feature flags:

```python
have = {'tls': 'on', 'logs': 'debug'}
want = {'tls': 'on', 'retries': '3'}
out, log = dict(have), []
for k, v in want.items():
    if k not in out:
        out[k] = v
        log.append('add ' + k)
    elif out[k] != v:
        out[k] = v
        log.append('update ' + k)
print(out)          # {'tls': 'on', 'logs': 'debug', 'retries': '3'}
print(sorted(log))  # ['add retries']
```

'logs' survives because want never mentions it, and 'tls' logs nothing because it already matched. Yours adds the None-means-absent branch.
