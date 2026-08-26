---
title: boto3 — find unattached EBS volumes
difficulty: easy
tier: packages
minutes: 25
prereqs: [57]
tags: [cloud, boto3]
practices: [8, 26, 57]
---
# boto3 — find unattached EBS volumes

*A detached EBS volume bills at full price forever and appears on no dashboard.*

Filed under topic 72. The checklist calls 72 "docker SDK vs shelling out", which cannot be drilled offline, so the number was free; topic 69 already holds the S3 public-access audit and these are two separate boto3 tasks.

## Why
The cloud bill keeps growing. One common cause is disk volumes (EBS) that were once attached to servers that have since been deleted. A detached volume still costs full price every month and shows up on no dashboard. The finance lead asks for a report: which volumes are attached to nothing, and how many gigabytes would be freed by removing them. A report only; deleting is a separate, reviewed step.

## You get
`ec2` — an AWS EC2 client object, the thing you call to ask about servers and their disks. The test hands in one connected to a fake in-memory AWS (moto) with a few servers, some attached disks and some orphan disks; nothing real is contacted.

## You return
a pair (tuple): a sorted list of `(volume_id, size_in_gb)` pairs for the unattached volumes, and the total of those sizes as a whole number (0 when there are none).

## Rules
Report the EBS volumes nobody is using, and what dropping them saves.

`ec2` is a boto3 EC2 client. `ec2.describe_volumes()` answers with a dict holding `"Volumes"`, a list of dicts. The fields that matter:

| field | what it holds |
| --- | --- |
| `"VolumeId"` | the id, e.g. `"vol-0a1b2c3d4e5f60718"` |
| `"Size"` | capacity in GB, an `int` |
| `"State"` | `"in-use"` while something has it attached, `"available"` once nothing does |
| `"Attachments"` | a list of attachment dicts, empty when nothing is attached |

Return the tuple `(orphans, reclaimable_gb)`:

- `orphans`: one `(volume_id, size_gb)` tuple per unattached volume, as a sorted list — sorting a list of tuples orders it by volume id
- `reclaimable_gb`: the sum of those sizes as an `int`, 0 when the list is empty

An account with two idle volumes and some in use would give:

```python
solve(ec2)
# -> ([("vol-0a1b2c3d4e5f60718", 100),
#      ("vol-0f9e8d7c6b5a40312", 8)], 108)
```

Two things to know about the fixture. Every instance in the account boots with a root volume, and those are attached — they must not appear in your answer. And an instance that is stopped still holds its volumes, so `"in-use"` is about attachment, not about whether anything is running.

> [!WARNING]
> This is a report, not a delete script. Do not call `delete_volume`; the test checks that every volume is still there when you are done.

## Hints
### Hint 1
The account has more volumes than the ones you would think to look for. Booting an instance quietly creates a root volume, so 'every volume in describe_volumes' is never the answer — you need the ones with nothing hanging off them. The other half of the job is the arithmetic: the sum has to be over the volumes you selected, not over the whole list, and that is the mistake that survives review because the number still looks plausible.
### Hint 2
One loop over ec2.describe_volumes()["Volumes"]. Keep a volume when its "Attachments" list is empty — an empty list is falsy, so `if not vol["Attachments"]` reads fine; testing vol["State"] == "available" gets you the same set. Append (vol["VolumeId"], vol["Size"]) tuples to a list, .sort() it, then sum the second item of each tuple with a generator expression. Return the two as a tuple.
### Hint 3
Different data — the same select-then-total shape over Elastic IPs, which also bill when nothing is using them:

```python
idle = []
for addr in ec2.describe_addresses()['Addresses']:
    if 'InstanceId' not in addr:
        idle.append((addr['AllocationId'], addr['PublicIp']))
idle.sort()
print(idle, len(idle) * 3.60)
```

Filter first into a list of tuples, sort, then derive the total from that list and never from the original. Yours totals Size instead of multiplying by a monthly rate.
