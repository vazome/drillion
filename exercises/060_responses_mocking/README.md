---
title: responses — mock the HTTP the code under test will make
minutes: 20
prereqs: [48]
tags: [testing, requests]
---
# responses — mock the HTTP the code under test will make

*A test that hits the real API is slow, flaky, and fails when someone else's cert expires.*

## Why
An inventory script (fetch_inventory, at the bottom of this file,
already written) talks to a hosts API: list the hosts, ask each one for
its CPU count, then post a report. To test it in CI without a real
server, you set up a fake server that answers exactly the requests the
script will make: the host list, one answer per host (some of them "404
gone"), and the report endpoint. The fake is strict: a request it was
not told about fails, and an answer you registered that the script never
asked for also fails. Your job: read the script, then register precisely
the answers it needs, built from a spec that changes every run.

## You get
`rsps` — the active fake server object (a
responses.RequestsMock). You register answers on it; the test then runs
the real script through it. Nothing real is contacted.
`spec` — a dict describing what the fake must answer, like
{"base_url": "https://inv.example.com", "token": "tok-4f9a",
"hosts": ["web-1", "db-2"], "cpu": {"web-1": 8}, "missing": ["db-2"],
"report_id": "rep-77"}.

## You return
nothing. The test calls fetch_inventory afterwards and
checks what it produced and which requests it made.

## Rules
Stand up the fake API that fetch_inventory needs, from `spec`.

fetch_inventory lives at the bottom of this file. It is already
written and you must not change it. Read it first: every request it
makes has to exist in the mock before it runs, or requests raises
ConnectionError.

`rsps` is an active responses.RequestsMock. Register endpoints on
it with rsps.add(...). `responses` is already imported up top.
`spec` says what each endpoint must answer:

```
spec = {"base_url": "https://inv.example.com",
        "token": "tok-4f9a",
        "hosts": ["web-1", "db-2"],   # the listing must return these
        "cpu": {"web-1": 8},          # these answer 200 with that cpu
        "missing": ["db-2"],          # these answer 404
        "report_id": "rep-77"}
```

For that spec, exactly four registrations must exist:

```
GET   https://inv.example.com/v1/hosts        200  {"hosts": ["web-1", "db-2"]}
GET   https://inv.example.com/v1/hosts/web-1  200  {"cpu": 8}
GET   https://inv.example.com/v1/hosts/db-2   404  body does not matter
POST  https://inv.example.com/v1/reports      200  {"id": "rep-77"}
```

and fetch_inventory(base_url, token) then returns

```
{"hosts": [{"name": "web-1", "cpu": 8},
           {"name": "db-2", "cpu": None}],
 "report_id": "rep-77"}
```

which is what the test checks. solve itself returns nothing — the
test calls fetch_inventory afterwards and grades the result.

Two rules the mock enforces:
  - Register every call the client makes. One it did not expect is
    a ConnectionError, not a 404.
  - Register nothing else. This mock is strict about unused
    registrations and fails at the end of the block if one never
    fired. So no shotgunning every host into every shape.

The spec varies each run: different host names, a different number
of missing ones, different cpu counts. Build the registrations by
walking the spec, not by typing them out.

## Hints
### Hint 1
The mock is a registry, not a proxy. Nothing is recorded or forwarded: you declare, up front, which (method, url) pairs exist and what each one answers, and any request outside that list fails. So the work is not really about the library — it is reading the client and listing the calls it will make, in the shapes it will make them: one listing call, one call per host, one write at the end. Notice which of those depend on data the previous response returned, because that decides what your listing registration has to say.
### Hint 2
rsps.add(responses.GET, url, json={...}, status=200) is the whole api. json= takes a Python object and serialises it; status= defaults to 200, so you only pass it for the 404s. responses.POST is how you register the write — a POST url registered as a GET will not match. The url argument is the full url with no query string; query params on the request are ignored when the registered url has none. Three loops and one plain registration will cover it.
### Hint 3
Different data — mocking a payments client that checks a balance then charges:

```python
with responses.RequestsMock() as rsps:
    rsps.add(responses.GET, 'https://pay.test/v1/balance',
             json={'cents': 500})
    rsps.add(responses.POST, 'https://pay.test/v1/charge', status=402)
    r = requests.get('https://pay.test/v1/balance', timeout=5)
    print(r.json())                     # {'cents': 500}
    print(requests.post('https://pay.test/v1/charge',
                        timeout=5).status_code)      # 402
    print(len(rsps.calls))              # 2
```

Yours is the same three arguments, just produced in a loop from the spec instead of written out one at a time.
