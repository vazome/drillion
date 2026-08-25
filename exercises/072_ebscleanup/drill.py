def solve(ec2):
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
_AZ = "us-east-1a"


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
    """Spec: how many instances, which extra volumes are attached, which idle."""
    sizes = [8, 16, 20, 50, 100, 200, 500]
    return {
        "instances": r.randint(2, 4),
        "attached": [r.choice(sizes) for _ in range(r.randint(1, 4))],
        "idle": [r.choice(sizes) for _ in range(r.randint(1, 5))],
        "stop_one": r.random() < 0.5,
    }


def _build(spec, ec2):
    """Materialise the account. Returns the sorted (id, size) truth for idle ones."""
    instances = []
    for _ in range(spec["instances"]):
        launched = ec2.run_instances(ImageId=_AMI, MinCount=1, MaxCount=1,
                                     InstanceType="t3.micro",
                                     Placement={"AvailabilityZone": _AZ})
        instances.append(launched["Instances"][0]["InstanceId"])

    for i, size in enumerate(spec["attached"]):
        volume = ec2.create_volume(AvailabilityZone=_AZ, Size=size)
        ec2.attach_volume(Device="/dev/sd{}".format(chr(ord("f") + i)),
                          InstanceId=instances[i % len(instances)],
                          VolumeId=volume["VolumeId"])

    idle = []
    for size in spec["idle"]:
        volume = ec2.create_volume(AvailabilityZone=_AZ, Size=size)
        idle.append((volume["VolumeId"], size))

    if spec["stop_one"]:
        ec2.stop_instances(InstanceIds=[instances[0]])
    return sorted(idle)


def _reference(ec2):
    orphans = []
    for volume in ec2.describe_volumes()["Volumes"]:
        if not volume["Attachments"]:
            orphans.append((volume["VolumeId"], volume["Size"]))
    orphans.sort()
    return orphans, sum(size for _, size in orphans)


def test_solve():
    r = rng()
    with _fake_aws_env():
        for _ in range(3):
            spec = _gen(r)
            with mock_aws():
                ec2 = boto3.client("ec2", region_name="us-east-1")
                idle = _build(spec, ec2)
                truth = (idle, sum(size for _, size in idle))
                total = len(ec2.describe_volumes()["Volumes"])

                assert _reference(ec2) == truth, "fixture drifted"
                assert solve(ec2) == truth, (
                    f"{len(idle)} of {total} volumes are unattached, {truth[1]} GB in total")
                assert len(ec2.describe_volumes()["Volumes"]) == total, (
                    "solve deleted volumes — this is a report, not a delete script")
