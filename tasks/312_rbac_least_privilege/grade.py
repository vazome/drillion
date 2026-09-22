"""What one sitting of 312 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds three
objects, `---`-separated, so they arrive here as a list. Every message here is what the
learner reads, so each one names the field and what it should have held."""

NAMESPACES = ["shop", "payments", "reporting"]
RESOURCES = [
    ("configmaps", "config-reader"),
    ("pods", "pod-watcher"),
    ("services", "service-lister"),
]
READ = {"get", "list", "watch"}
RBAC = "rbac.authorization.k8s.io"


def brief(r):
    resource, role = r.choice(RESOURCES)
    return {
        "namespace": r.choice(NAMESPACES),
        "resource": resource,
        "role": role,
        "account": r.choice(["reporter", "sidecar", "dashboard"]),
    }


def _object(doc, which, kind, name, b):
    assert doc.get("kind") == kind, (
        f"the {which} document is a {doc.get('kind')}, and it should be the {kind}"
    )
    meta = doc.get("metadata", {})
    assert meta.get("name") == name, (
        f"the {kind}'s metadata.name is {meta.get('name')!r}, and it should be {name!r}"
    )
    assert meta.get("namespace") == b["namespace"], (
        f"the {kind}'s metadata.namespace is {meta.get('namespace')!r}, and it should be "
        f"{b['namespace']!r}"
    )


def check_many(docs, b):
    assert len(docs) == 3, (
        f"the file holds {len(docs)} documents, and the task asks for three: the "
        "ServiceAccount, the Role and the RoleBinding"
    )
    account, role, binding = docs
    _object(account, "first", "ServiceAccount", b["account"], b)

    _object(role, "second", "Role", b["role"], b)
    rules = role.get("rules") or []
    assert len(rules) == 1, f"the Role has {len(rules)} rules, and the task asks for one"
    rule = rules[0]
    assert rule.get("apiGroups") == [""], (
        f"the rule's apiGroups is {rule.get('apiGroups')!r}, and {b['resource']} live in "
        "the core group, written ['']"
    )
    assert rule.get("resources") == [b["resource"]], (
        f"the rule's resources is {rule.get('resources')!r}, and it should be "
        f"[{b['resource']!r}] alone"
    )
    verbs = set(rule.get("verbs") or [])
    assert verbs == READ, (
        f"the rule allows {sorted(verbs)}, and reading is exactly get, list and watch: "
        + (
            f"{sorted(verbs - READ)} would let it change things"
            if verbs - READ
            else f"it is missing {sorted(READ - verbs)}"
        )
    )

    _object(binding, "third", "RoleBinding", b["role"], b)
    ref = binding.get("roleRef") or {}
    want = {"apiGroup": RBAC, "kind": "Role", "name": b["role"]}
    got = {k: ref.get(k) for k in want}
    assert got == want, f"roleRef is {got}, and it should be {want}"
    subjects = binding.get("subjects") or []
    assert len(subjects) == 1, (
        f"the binding has {len(subjects)} subjects, and the task asks for one"
    )
    want = {"kind": "ServiceAccount", "name": b["account"], "namespace": b["namespace"]}
    got = {k: subjects[0].get(k) for k in want}
    assert got == want, f"the subject is {got}, and it should be {want}"
