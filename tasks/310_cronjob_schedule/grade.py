"""What one sitting of 310 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held.

`schedule` is not shown to the learner, who writes it from `time`: it is the answer key's."""

NAMES = ["nightly-backup", "daily-report", "purge-sessions", "sync-catalog"]
IMAGES = ["ghcr.io/acme/tools:3.2", "postgres:17", "ghcr.io/acme/reports:1.4"]
ZONES = ["Europe/Berlin", "America/New_York", "Asia/Tokyo", "Etc/UTC"]


def brief(r):
    hour, minute = r.randint(0, 23), r.choice([0, 5, 15, 30, 45])
    return {
        "name": r.choice(NAMES),
        "image": r.choice(IMAGES),
        "time": f"{hour:02}:{minute:02}",
        "schedule": f"{minute} {hour} * * *",
        "timeZone": r.choice(ZONES),
        "keep": r.choice([3, 5]),
        "keepFailed": r.choice([1, 2]),
    }


def check(doc, b):
    assert doc.get("kind") == "CronJob", (
        f"this is a {doc.get('kind')}, and the task asks for a CronJob"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})

    fields = str(spec.get("schedule", "")).split()
    hour, minute = (int(part) for part in b["time"].split(":"))
    assert len(fields) == 5, (
        f"spec.schedule is {spec.get('schedule')!r}, and a cron schedule has five fields"
    )
    assert fields[2:] == ["*", "*", "*"], (
        f"spec.schedule is {spec.get('schedule')!r}: the last three fields limit the days, "
        "and every day means all three are '*'"
    )
    got = [int(f) if f.isdigit() else f for f in fields[:2]]
    assert got == [minute, hour], (
        f"spec.schedule is {spec.get('schedule')!r}, which is not {b['time']}: minute "
        f"comes first, so it should start {minute} {hour}"
    )
    assert spec.get("timeZone") == b["timeZone"], (
        f"spec.timeZone is {spec.get('timeZone')!r}, and it should be {b['timeZone']!r}"
    )
    assert spec.get("concurrencyPolicy") == "Forbid", (
        f"spec.concurrencyPolicy is {spec.get('concurrencyPolicy')!r}, and it should be "
        "'Forbid': the default lets a slow run and the next one overlap"
    )
    for key, want in (
        ("successfulJobsHistoryLimit", b["keep"]),
        ("failedJobsHistoryLimit", b["keepFailed"]),
    ):
        assert spec.get(key) == want, f"spec.{key} is {spec.get(key)!r}, and it should be {want}"

    pod = (
        spec.get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {})
    )
    containers = pod.get("containers") or []
    assert len(containers) == 1, (
        f"the Job template's pod has {len(containers)} containers, and the task asks for one"
    )
    assert containers[0].get("image") == b["image"], (
        f"the container image is {containers[0].get('image')!r}, not {b['image']!r}"
    )
    policy = pod.get("restartPolicy")
    assert policy in ("Never", "OnFailure"), (
        f"the pod's restartPolicy is {policy!r}, and a Job's pod needs 'Never' or "
        "'OnFailure'"
    )
