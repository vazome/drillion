"""What one sitting of 361 asks for, and what counts as having answered it.

The delete policy is a comma-separated annotation, read as Argo CD reads it: a set, so the
order the two names come in does not matter."""

APPS = ["checkout", "payments", "orders", "catalog"]
HOOK = "argocd.argoproj.io/hook"
DELETE = "argocd.argoproj.io/hook-delete-policy"
POLICIES = {"BeforeHookCreation", "HookSucceeded"}


def brief(r):
    name = r.choice(APPS)
    return {
        "name": name,
        "job": f"{name}-migrate",
        "db": f"{name}-db",
        "image": f"ghcr.io/acme/{name}:{r.choice(['3.2.0', '1.9.4', '2.0.1'])}",
        "retries": r.choice([1, 2, 3]),
    }


def _annotations(doc):
    return (doc.get("metadata") or {}).get("annotations") or {}


def _one_container(doc, kind):
    containers = (
        ((doc.get("spec") or {}).get("template") or {}).get("spec") or {}
    ).get("containers") or []
    assert len(containers) == 1, (
        f"the {kind}'s pod template has {len(containers)} containers, and it should have one"
    )
    return containers[0]


def check_many(docs, b):
    assert len(docs) == 2, (
        f"the file holds {len(docs)} documents, and the task asks for two: the Job, then "
        "the Deployment"
    )
    job, deploy = docs

    assert job.get("kind") == "Job", (
        f"the first document is a {job.get('kind')}, and it should be the Job"
    )
    name = (job.get("metadata") or {}).get("name")
    assert name == b["job"], f"the Job's metadata.name is {name!r}, and it should be {b['job']!r}"
    notes = _annotations(job)
    assert notes.get(HOOK) == "PreSync", (
        f"the Job's {HOOK} is {notes.get(HOOK)!r}, and it should be 'PreSync': without "
        "it the Job is applied with everything else, not before it"
    )
    given = {p.strip() for p in str(notes.get(DELETE, "")).split(",") if p.strip()}
    assert given == POLICIES, (
        f"the Job's {DELETE} is {notes.get(DELETE)!r}, and it should name "
        "BeforeHookCreation and HookSucceeded: "
        + (
            "without HookSucceeded every finished migration stays in the cluster"
            if "HookSucceeded" not in given
            else "naming a policy drops the BeforeHookCreation default, and a failed Job "
            "would then block the next sync"
            if "BeforeHookCreation" not in given
            else "HookFailed would delete a failed Job and its logs before anyone reads them"
        )
    )
    spec = job.get("spec") or {}
    assert spec.get("backoffLimit") == b["retries"], (
        f"the Job's backoffLimit is {spec.get('backoffLimit')!r}, and it should be "
        f"{b['retries']}"
    )
    restart = ((spec.get("template") or {}).get("spec") or {}).get("restartPolicy")
    assert restart == "Never", (
        f"the Job's pod has restartPolicy {restart!r}, and it should be 'Never'"
    )
    c = _one_container(job, "Job")
    assert c.get("name") == "migrate", (
        f"the Job's container is named {c.get('name')!r}, and it should be 'migrate'"
    )
    assert c.get("image") == b["image"], (
        f"the migration runs {c.get('image')!r}, and it should run the release's own "
        f"image, {b['image']!r}"
    )
    assert c.get("args") == ["migrate", "up"], (
        f"the Job's args are {c.get('args')!r}, and they should be ['migrate', 'up']"
    )
    env = c.get("env") or []
    want = [{"name": "DATABASE_HOST", "value": b["db"]}]
    assert env == want, f"the Job's env is {env}, and it should be {want}"

    assert deploy.get("kind") == "Deployment", (
        f"the second document is a {deploy.get('kind')}, and it should be the Deployment"
    )
    name = (deploy.get("metadata") or {}).get("name")
    assert name == b["name"], (
        f"the Deployment's metadata.name is {name!r}, and it should be {b['name']!r}"
    )
    assert HOOK not in _annotations(deploy), (
        "the Deployment is annotated as a hook, and it is the release itself: Argo CD "
        "keeps it applied, so it takes no hook annotation"
    )
    spec = deploy.get("spec") or {}
    assert spec.get("replicas") == 2, (
        f"the Deployment's replicas is {spec.get('replicas')!r}, and it should be 2"
    )
    selector = (spec.get("selector") or {}).get("matchLabels")
    labels = ((spec.get("template") or {}).get("metadata") or {}).get("labels") or {}
    assert selector == {"app": b["name"]} and labels.get("app") == b["name"], (
        f"the Deployment selects {selector} and labels its pods {labels}, and both should "
        f"be app: {b['name']!r}"
    )
    c = _one_container(deploy, "Deployment")
    assert c.get("name") == b["name"] and c.get("image") == b["image"], (
        f"the Deployment's container is {c.get('name')!r} running {c.get('image')!r}, and "
        f"it should be {b['name']!r} running {b['image']!r}"
    )
