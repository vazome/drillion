"""The fixture manifest task every phase-1 test grades against. It never enters tasks/."""

import sys

README = """\
---
title: A fixture deployment
kind: manifest
difficulty: easy
minutes: 10
track: kubernetes
tags: [deployment]
---
# A fixture deployment

## Why
Because a Deployment is the first shape anyone has to type from nothing.

## You get
Nothing but the requirements below.

## You return
a Deployment named `{name}` with {replicas} replicas.

## Rules
One document, one Deployment.

## Hints
### Hint 1
one
### Hint 2
two
### Hint 3
three
"""

GRADE = """\
SERVICES = ["checkout", "billing"]


def brief(r):
    return {"name": r.choice(SERVICES), "replicas": r.randint(2, 5)}


def check(doc, b):
    assert doc["kind"] == "Deployment", "kind"
    assert doc["metadata"]["name"] == b["name"], "name"
    assert doc["spec"]["replicas"] == b["replicas"], "replicas"
"""

SOLUTION = """\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: {replicas}
"""


def fixture_task():
    """{filename: text} for `tests.fixtures.tasks_root`."""
    return {
        "README.md": README,
        "task.yaml": "",
        "grade.py": GRADE,
        "solution.yaml": SOLUTION,
    }


# The pins are empty until the release gate, so `tools.installed` answers None and every
# test that touches the grading path would skip. This stands in: the same invocation, the
# same JSON report, the same exit codes, and it refuses an invocation it did not expect so
# that a harness that stops passing `-strict` fails a test rather than passing quietly.
STUB_KUBECONFORM = """#!{python}
import json
import re
import sys

args = sys.argv[1:]
expected = [
    "-strict",
    "-kubernetes-version",
    {kube!r},
    "-schema-location",
    {schemas!r},
    "-output",
    "json",
]
if args[:-1] != expected:
    sys.stderr.write("kubeconform: unexpected invocation: " + " ".join(args))
    raise SystemExit(2)

# The real shapes, not tidied up: `msg` is boilerplate naming the schema's install path
# whatever went wrong, the per-field detail lives in `validationErrors`, and a kind with no
# packaged schema is a `statusError` carrying neither.
BOILERPLATE = (
    "problem validating schema. Check JSON formatting: jsonschema validation failed "
    "with 'file://{schemas}#'"
)
text = open(args[-1], encoding="utf-8").read()
kind = re.search(r"^kind:[ \\t]*(\\S+)", text, re.M)
resource = {{"filename": args[-1], "status": "statusValid"}}
if kind is None or kind.group(1) != "Deployment":
    resource |= {{
        "status": "statusError",
        "msg": "could not find schema for " + (kind.group(1) if kind else ""),
    }}
elif 'replicas: "' in text:
    resource |= {{
        "status": "statusInvalid",
        "msg": BOILERPLATE,
        "validationErrors": [
            {{"path": "/spec/replicas", "msg": "expected integer, but got string"}}
        ],
    }}
elif "apiVersion:" not in text:
    # not every rejection is a field comparison, so this one carries no validationErrors
    resource |= {{"status": "statusInvalid", "msg": BOILERPLATE}}
print(json.dumps({{"resources": [resource]}}))
raise SystemExit(0 if resource["status"] == "statusValid" else 1)
"""


def stub_kubeconform(root):
    """The stand-in, installed where a real one would live: under `tools/`, which is the
    one directory a graded run is allowed to execute from."""
    from drillion import tools

    path = root / "tools" / "kubeconform"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        STUB_KUBECONFORM.format(
            python=sys.executable,
            kube=tools.KUBERNETES_VERSION,
            schemas=tools.schema_location(),
        ),
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path
