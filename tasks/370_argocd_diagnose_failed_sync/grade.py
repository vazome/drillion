"""What 370 asks for, and what counts as having answered it.

The evidence names fixed objects, so the brief is empty. The answer is the Job from git with
one value fixed; the likely wrong fixes get their own message first, and anything else that
moved is named by the first path where it differs."""

HOOK = "argocd.argoproj.io/hook"
DELETE = "argocd.argoproj.io/hook-delete-policy"
IMAGE = "ghcr.io/acme/orders:5.1.0"
WANT = {
    "apiVersion": "batch/v1",
    "kind": "Job",
    "metadata": {
        "name": "orders-migrate",
        "annotations": {HOOK: "PreSync", DELETE: "BeforeHookCreation,HookSucceeded"},
    },
    "spec": {
        "backoffLimit": 2,
        "template": {
            "spec": {
                "restartPolicy": "Never",
                "containers": [
                    {
                        "name": "migrate",
                        "image": IMAGE,
                        "args": ["migrate", "up"],
                        "env": [{"name": "DATABASE_HOST", "value": "orders-db"}],
                    }
                ],
            }
        },
    },
}


def brief(r):
    return {}


def difference(got, want, path=""):
    """The first place `got` leaves `want`, in words, or None when they match."""
    here = path or "the document"
    if isinstance(want, dict):
        if not isinstance(got, dict):
            return f"{here} is {got!r}, and in git it is a mapping"
        for key in want:
            if key not in got:
                return f"{path}.{key} is missing, and git has it".lstrip(".")
        for key in got:
            if key not in want:
                return f"{path}.{key} is not in git's manifest; leave it out".lstrip(".")
        for key in want:
            found = difference(got[key], want[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(want, list):
        if not isinstance(got, list) or len(got) != len(want):
            return f"{here} is {got!r}, and it should be {want!r}".lstrip(".")
        for i, (g, w) in enumerate(zip(got, want)):
            found = difference(g, w, f"{path}[{i}]")
            if found:
                return found
        return None
    if got != want:
        return f"{here} is {got!r}, and it should be {want!r}".lstrip(".")
    return None


def check(doc, b):
    assert doc.get("kind") == "Job", f"kind is {doc.get('kind')!r}, and the fix is to the Job"
    notes = (doc.get("metadata") or {}).get("annotations") or {}
    assert notes.get(HOOK) == "PreSync", (
        f"the Job's {HOOK} is {notes.get(HOOK)!r}: without PreSync the migration would run "
        "alongside the new release instead of before it"
    )
    containers = (
        ((doc.get("spec") or {}).get("template") or {}).get("spec") or {}
    ).get("containers") or [{}]
    c = containers[0] if isinstance(containers[0], dict) else {}
    env = {e.get("name"): e.get("value") for e in c.get("env") or [] if isinstance(e, dict)}
    host = env.get("DATABASE_HOST")
    assert host != "postgres", (
        "DATABASE_HOST is still 'postgres', the name the log says DNS cannot find"
    )
    assert host == "orders-db", (
        f"DATABASE_HOST is {host!r}, and the database's Service in the namespace is "
        "'orders-db'"
    )
    found = difference(doc, WANT)
    assert found is None, found
