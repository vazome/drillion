"""The fixture manifest task every phase-1 test grades against. It never enters tasks/."""

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
