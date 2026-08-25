"""A detached EBS volume bills at full price forever and appears on no dashboard.

Filed under topic 72. The checklist calls 72 "docker SDK vs shelling out",
which cannot be drilled offline, so the number was free; topic 69 already
holds the S3 public-access audit and these are two separate boto3 tasks.
"""

import contextlib
import os

import boto3
from _lib import rng
from moto import mock_aws

META = {"topic": 72, "title": "boto3 task — find unattached EBS volumes",
        "tier": 4, "minutes": 25, "prereqs": [68],
        "practices": [9, 28, 68]}


def solve(ec2):
    """WHY: The cloud bill keeps growing. One common cause is disk volumes
    (EBS) that were once attached to servers that have since been deleted.
    A detached volume still costs full price every month and shows up on no
    dashboard. The finance lead asks for a report: which volumes are
    attached to nothing, and how many gigabytes would be freed by removing
    them. A report only; deleting is a separate, reviewed step.

    YOU GET: `ec2` — an AWS EC2 client object, the thing you call to ask
    about servers and their disks. The test hands in one connected to a
    fake in-memory AWS (moto) with a few servers, some attached disks and
    some orphan disks; nothing real is contacted.

    YOU RETURN: a pair (tuple): a sorted list of (volume_id, size_in_gb)
    pairs for the unattached volumes, and the total of those sizes as a
    whole number (0 when there are none).

    ─── exact rules ───
    Report the EBS volumes nobody is using, and what dropping them saves.

    `ec2` is a boto3 EC2 client. `ec2.describe_volumes()` answers with a dict
    holding "Volumes", a list of dicts. The fields that matter:

      - "VolumeId"    — the id, e.g. "vol-0a1b2c3d4e5f60718"
      - "Size"        — capacity in GB, an int
      - "State"       — "in-use" while something has it attached,
                        "available" once nothing does
      - "Attachments" — a list of attachment dicts, empty when nothing
                        is attached

    Return the tuple (orphans, reclaimable_gb):

      - orphans: one (volume_id, size_gb) tuple per unattached volume,
        as a sorted list — sorting a list of tuples orders it by volume id
      - reclaimable_gb: the sum of those sizes as an int, 0 when the list
        is empty

    An account with two idle volumes and some in use would give:

        ([("vol-0a1b2c3d4e5f60718", 100),
          ("vol-0f9e8d7c6b5a40312", 8)], 108)

    Two things to know about the fixture. Every instance in the account boots
    with a root volume, and those are attached — they must not appear in your
    answer. And an instance that is stopped still holds its volumes, so
    "in-use" is about attachment, not about whether anything is running.

    This is a report, not a delete script. Do not call delete_volume; the
    test checks that every volume is still there when you are done.
    """
    raise NotImplementedError


HINTS = [
    ("The account has more volumes than the ones you would think to look for. "
    "Booting an instance quietly creates a root volume, so 'every volume in "
    "describe_volumes' is never the answer — you need the ones with nothing "
    "hanging off them. The other half of the job is the arithmetic: the sum "
    "has to be over the volumes you selected, not over the whole list, and "
    "that is the mistake that survives review because the number still looks "
    "plausible."),
    ("One loop over ec2.describe_volumes()[\"Volumes\"]. Keep a volume when its "
    "\"Attachments\" list is empty — an empty list is falsy, so `if not "
    "vol[\"Attachments\"]` reads fine; testing vol[\"State\"] == \"available\" "
    "gets you the same set. Append (vol[\"VolumeId\"], vol[\"Size\"]) tuples to "
    "a list, .sort() it, then sum the second item of each tuple with a "
    "generator expression. Return the two as a tuple."),
    ("Different data — the same select-then-total shape over Elastic IPs, "
    "which also bill when nothing is using them:\n"
    "    idle = []\n"
    "    for addr in ec2.describe_addresses()['Addresses']:\n"
    "        if 'InstanceId' not in addr:\n"
    "            idle.append((addr['AllocationId'], addr['PublicIp']))\n"
    "    idle.sort()\n"
    "    print(idle, len(idle) * 3.60)\n"
    "Filter first into a list of tuples, sort, then derive the total from "
    "that list and never from the original. Yours totals Size instead of "
    "multiplying by a monthly rate."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
