def solve(ec2, required: list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import contextlib
import os

import boto3
from _lib import rng
from moto import mock_aws

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
