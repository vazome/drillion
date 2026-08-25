"""Untagged instances are the ones nobody can bill, page, or safely delete."""

import contextlib
import os

import boto3
from _lib import rng
from moto import mock_aws

META = {"topic": 71, "title": "boto3 task — audit EC2 instances for missing tags",
        "tier": 4, "minutes": 25, "prereqs": [68],
        "practices": [18, 20, 68], "tags": ["cloud", "boto3"]}


def solve(ec2, required):
    """WHY: Every server in the cloud account is supposed to carry labels
    (tags) like Owner and CostCenter, so finance can bill the right team and
    on-call knows who to wake. Servers launched without them are the ones
    nobody can bill, page, or safely delete. The platform team asks for an
    audit: for each mandatory label, which servers are missing it. A label
    that is present but set to an empty value counts as missing, since
    "Owner: " helps nobody.

    YOU GET: `ec2` — an AWS EC2 client object. The test hands in one
    connected to a fake in-memory AWS (moto) with a small fleet launched
    with various tags; nothing real is contacted.
    `required` — a list of the mandatory tag names, like ["CostCenter",
    "Owner"].

    YOU RETURN: a dict with one entry per required tag name, mapping it to
    a sorted list of the ids of the servers missing it (an empty list when
    none are).

    ─── exact rules ───
    Report which instances are missing which mandatory tags.

    `ec2` is a boto3 EC2 client. `required` is the list of tag keys every
    instance is supposed to carry, e.g. ["CostCenter", "Owner"].

    `ec2.describe_instances()` does not answer with a flat list of instances.
    It answers with the API's own shape:

        {"Reservations": [
            {"ReservationId": "r-...", "Instances": [ {...}, {...} ]},
            {"ReservationId": "r-...", "Instances": [ {...} ]},
        ]}

    One launch makes one reservation, and launching five instances at once
    puts all five inside that single reservation. So both loops are load
    bearing.

    Each instance dict has "InstanceId", and — only if it has any tags at
    all — a "Tags" list of {"Key": ..., "Value": ...} dicts. An instance
    launched with no tags has no "Tags" key whatsoever.

    A required tag counts as missing when its key is absent, and also when
    the key is there but its value is the empty string. "Owner" with nothing
    after it satisfies no auditor.

    Return a dict with one entry per required tag key, mapping that key to
    the sorted list of ids of the instances missing it. Keep the entry even
    when the list is empty:

        required = ["CostCenter", "Environment", "Owner"]
        ->  {"CostCenter": ["i-0a1b2c3d4e5f60718", "i-0f9e8d7c6b5a40312"],
             "Environment": [],
             "Owner": ["i-0f9e8d7c6b5a40312"]}

    Ids that appear under two keys are not a mistake — that instance is
    missing both. Read only: do not launch, tag, stop or terminate anything.
    """
    raise NotImplementedError


HINTS = [
    ("The response shape is the trap. Instances are nested one level deeper "
    "than you want them, inside reservations, and a reservation holds every "
    "instance from one launch. So code that walks the reservations and looks "
    "at Instances[0] audits one machine per launch and calls the other four "
    "compliant. Two smaller traps sit underneath: an instance with no tags "
    "has no Tags key at all, so indexing it raises rather than returning an "
    "empty list, and a tag set to the empty string is present in the response "
    "but does not count as tagged."),
    ("Seed the answer first: {key: [] for key in required}, so a tag nobody is "
    "missing still comes back with an empty list. Then two nested for loops — "
    "reservations on the outside, reservation[\"Instances\"] on the inside. "
    "For each instance, flatten its tags into a dict with a comprehension "
    "over instance.get(\"Tags\", []) keyed on t[\"Key\"]. Then one pass over "
    "`required`: `if not tags.get(key)` is true for both the absent key and "
    "the empty value. Sort each list before you return."),
    ("Different data — the same two-level walk over autoscaling groups, "
    "collecting the instances a group considers unhealthy:\n"
    "    sick = {}\n"
    "    for group in asg.describe_auto_scaling_groups()['AutoScalingGroups']:\n"
    "        name = group['AutoScalingGroupName']\n"
    "        sick[name] = []\n"
    "        for member in group['Instances']:\n"
    "            if member['HealthStatus'] != 'Healthy':\n"
    "                sick[name].append(member['InstanceId'])\n"
    "        sick[name].sort()\n"
    "    print(sick)    # {'api-asg': ['i-03', 'i-09'], 'worker-asg': []}\n"
    "Note the group with nothing wrong still gets a key, because the key was "
    "written before the inner loop ran. Yours writes the required tag keys up "
    "front for exactly the same reason."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

_FAKE_AWS = {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
             "AWS_SECURITY_TOKEN": "testing", "AWS_SESSION_TOKEN": "testing",
             "AWS_DEFAULT_REGION": "us-east-1"}

_AMI = "ami-0abcdef1234567890"


@contextlib.contextmanager
def _fake_aws_env():
    """Junk credentials, so a call that escaped the mock could not authenticate."""
    saved = {k: os.environ.get(k) for k in _FAKE_AWS}
    os.environ.update(_FAKE_AWS)
    try:
        yield
    finally:
        for key, old in saved.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


def _gen(r):
    """Spec: (required keys, [(instances_per_launch, tag list or None), ...])."""
    pool = ["Owner", "Environment", "CostCenter", "Team", "Project"]
    r.shuffle(pool)
    required = sorted(pool[:r.randint(2, 4)])
    spare = ["Name", "ManagedBy", "Schedule"]

    def value():
        return r.choice(["alice", "bob", "carol", "prod", "staging", "cc-1120",
                         "platform", "payments", "sandbox"])

    def tags(absent=(), blank=()):
        out = [{"Key": k, "Value": "" if k in blank else value()}
               for k in required if k not in absent]
        if r.random() < 0.5:
            out.append({"Key": r.choice(spare), "Value": value()})
        r.shuffle(out)
        return out

    plan = [
        (r.randint(2, 3), tags()),                        # one launch, several
        (1, tags(absent=[r.choice(required)])),           # a key simply not set
        (1, tags(blank=[r.choice(required)])),            # a key set to ""
    ]
    if r.random() < 0.55:
        plan.append((1, None))                            # launched with no tags
    for _ in range(r.randint(0, 2)):
        plan.append((r.randint(1, 2),
                     tags(absent=[k for k in required if r.random() < 0.4])))
    r.shuffle(plan)
    return required, plan


def _build(plan, ec2):
    """Launch the fleet. Returns [(instance_id, the tags it really got), ...]."""
    made = []
    for count, tags in plan:
        kwargs = {"ImageId": _AMI, "MinCount": count, "MaxCount": count,
                  "InstanceType": "t3.micro"}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "instance",
                                            "Tags": tags}]
        for instance in ec2.run_instances(**kwargs)["Instances"]:
            made.append((instance["InstanceId"], tags or []))
    return made


def _truth(made, required):
    """Ground truth straight from the spec, never from the API."""
    out = {key: [] for key in required}
    for instance_id, tags in made:
        present = {t["Key"]: t["Value"] for t in tags}
        for key in required:
            if not present.get(key):
                out[key].append(instance_id)
    for ids in out.values():
        ids.sort()
    return out


def _reference(ec2, required):
    missing = {key: [] for key in required}
    for reservation in ec2.describe_instances()["Reservations"]:
        for instance in reservation["Instances"]:
            tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
            for key in required:
                if not tags.get(key):
                    missing[key].append(instance["InstanceId"])
    for ids in missing.values():
        ids.sort()
    return missing


def test_solve():
    r = rng()
    with _fake_aws_env():
        for _ in range(4):
            required, plan = _gen(r)
            with mock_aws():
                ec2 = boto3.client("ec2", region_name="us-east-1")
                made = _build(plan, ec2)
                truth = _truth(made, required)

                assert _reference(ec2, required) == truth, "fixture drifted"
                assert solve(ec2, required) == truth, (
                    f"{len(made)} instances across {len(plan)} launches, required tags {required}")
