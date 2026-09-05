import sys


def solve(version: str, host: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from unittest.mock import patch

from _lib import rng


def send_alert(url, payload):
    """The real call. In a test it must never get this far."""
    raise RuntimeError(f"send_alert really tried to POST to {url} — patch it")


def run_deploy(version, host):
    """The code under test. It looks up send_alert in this module's globals."""
    reply = send_alert(f"https://{host}/hooks/deploy",
                       {"version": version, "status": "done"})
    return f"{version} {reply['status']}"


def _gen(r):
    version = f"v{r.randint(1, 9)}.{r.randint(0, 20)}.{r.randint(0, 9)}"
    host = r.choice(["hooks.internal", "alerts.prod", "chatops.eu"])
    return version, f"{host}:{r.choice([80, 443, 8080])}"


def _reference(version, host):
    with patch.object(sys.modules[__name__], "send_alert") as fake:
        fake.return_value = {"status": "ok"}
        result = run_deploy(version, host)
        url, payload = fake.call_args.args
        return {"result": result, "calls": fake.call_count,
                "url": url, "payload": payload}


def test_solve():
    r = rng()
    for _ in range(4):
        version, host = _gen(r)
        got = solve(version, host)
        assert got == _reference(version, host)

        try:                                    # the patch has to be gone
            send_alert("https://example.invalid/x", {})
        except RuntimeError:
            pass
        else:
            raise AssertionError("send_alert is still patched after solve returned")
