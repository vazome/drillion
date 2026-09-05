---
title: boto3 — audit EC2 instances for missing tags
difficulty: medium
tier: packages
minutes: 25
prereqs: [4, 57]
tags: [cloud, boto3]
---
# boto3 — audit EC2 instances for missing tags

*Untagged instances are the ones nobody can bill, page, or safely delete.*

## Read first
- [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) — paginators — tag listings are paginated

## Why
Every server in the cloud account is supposed to carry labels (tags) like Owner and CostCenter, so finance can bill the right team and on-call knows who to wake. Servers launched without them are the ones nobody can bill, page, or safely delete. The platform team asks for an audit: for each mandatory label, which servers are missing it. A label that is present but set to an empty value counts as missing, since "Owner: " helps nobody.

## You get
`ec2` — an AWS EC2 client object. The test hands in one connected to a fake in-memory AWS (moto) with a small fleet launched with various tags; nothing real is contacted.

`required` — a list of the mandatory tag names, like `["CostCenter", "Owner"]`.

## You return
a dict with one entry per required tag name, mapping it to a sorted list of the ids of the servers missing it (an empty list when none are).

## Rules
Report which instances are missing which mandatory tags.

`ec2` is a boto3 EC2 client. `required` is the list of tag keys every instance is supposed to carry, e.g. `["CostCenter", "Owner"]`.

`ec2.describe_instances()` does not answer with a flat list of instances. It answers with the API's own shape:

```python
{"Reservations": [
    {"ReservationId": "r-...", "Instances": [ {...}, {...} ]},
    {"ReservationId": "r-...", "Instances": [ {...} ]},
]}
```

One launch makes one reservation, and launching five instances at once puts all five inside that single reservation. So both loops are load bearing.

Each instance dict has `"InstanceId"`, and — only if it has any tags at all — a `"Tags"` list of `{"Key": ..., "Value": ...}` dicts. An instance launched with no tags has no `"Tags"` key whatsoever.

A required tag counts as missing when its key is absent, and also when the key is there but its value is the empty string. "Owner" with nothing after it satisfies no auditor.

Return a dict with one entry per required tag key, mapping that key to the sorted list of ids of the instances missing it. Keep the entry even when the list is empty:

```python
solve(ec2, ["CostCenter", "Environment", "Owner"])
# -> {"CostCenter": ["i-0a1b2c3d4e5f60718", "i-0f9e8d7c6b5a40312"],
#     "Environment": [],
#     "Owner": ["i-0f9e8d7c6b5a40312"]}
```

Ids that appear under two keys are not a mistake — that instance is missing both.

> [!WARNING]
> Read only: do not launch, tag, stop or terminate anything.

## Hints
### Hint 1
The response shape is the trap. Instances are nested one level deeper than you want them, inside reservations, and a reservation holds every instance from one launch. So code that walks the reservations and looks at Instances[0] audits one machine per launch and calls the other four compliant. Two smaller traps sit underneath: an instance with no tags has no Tags key at all, so indexing it raises rather than returning an empty list, and a tag set to the empty string is present in the response but does not count as tagged.
### Hint 2
Seed the answer first: {key: [] for key in required}, so a tag nobody is missing still comes back with an empty list. Then two nested for loops — reservations on the outside, reservation["Instances"] on the inside. For each instance, flatten its tags into a dict with a comprehension over instance.get("Tags", []) keyed on t["Key"]. Then one pass over `required`: `if not tags.get(key)` is true for both the absent key and the empty value. Sort each list before you return.
### Hint 3
Different data — the same two-level walk over autoscaling groups, collecting the instances a group considers unhealthy:

```python
sick = {}
for group in asg.describe_auto_scaling_groups()['AutoScalingGroups']:
    name = group['AutoScalingGroupName']
    sick[name] = []
    for member in group['Instances']:
        if member['HealthStatus'] != 'Healthy':
            sick[name].append(member['InstanceId'])
    sick[name].sort()
print(sick)    # {'api-asg': ['i-03', 'i-09'], 'worker-asg': []}
```

Note the group with nothing wrong still gets a key, because the key was written before the inner loop ran. Yours writes the required tag keys up front for exactly the same reason.
