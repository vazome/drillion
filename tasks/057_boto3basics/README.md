---
title: boto3 — client vs resource, and paginators
difficulty: medium
tier: packages
minutes: 20
prereqs: [2, 9]
tags: [cloud, boto3]
---
# boto3 — client vs resource, and paginators

*Every AWS list call answers with one page; the rest of the account is on page two.*

## Read first
- [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) — clients vs resources, and where the operation names come from

## Why
Finance asks "how much is stored in the logs bucket, and what exactly is in it?". AWS answers list requests one page at a time, about a thousand entries per page, and only quietly notes that more exist. A script that reads one page reports a fraction of the bucket, and nobody notices until the bill disagrees with the report. You are asked for the full list of object names and the total size, walking every page.

## You get
`s3` — an AWS S3 client object, the thing you call to talk to the storage service. The test hands in one connected to a fake in-memory AWS (moto), so nothing real is contacted and no money is spent.

`bucket` — a string bucket name like `"acme-logs-412"`. It already exists and holds more objects than a single page returns.

## You return
a pair (tuple): a sorted list of every object name (strings), and the total size in bytes as a whole number.

## Rules
Report every object in a bucket that is bigger than one page.

`s3` is a boto3 S3 *client*: a thin skin over the HTTP API where one method call is one request and every answer is a plain dict. The other flavour, `boto3.resource("s3")`, wraps the same API in objects and hides the paging from you. The client is the one interviews ask about, and the one where the paging is your problem, so work with it here.

`bucket` is the name of a bucket that already exists and already holds more objects than a single API call will hand back.

Return the tuple `(keys, total_bytes)`:

- `keys`: every object key in the bucket, as a sorted list of strings
- `total_bytes`: the sum of every object's `Size`, as an `int`

A bucket holding three objects would give:

```python
solve(s3, bucket)
# -> (["logs/a.log", "logs/b.log", "raw/c.json"], 4096)
```

The response dict from a list call puts the objects under `"Contents"`, and each one is itself a dict with `"Key"` and `"Size"` among other fields. A page with nothing on it has no `"Contents"` key at all, so reach for it with `.get`.

> [!WARNING]
> Asking for a bigger page does not get you the whole bucket — the service caps the page size and ignores you. Do not create or delete anything.

## Hints
### Hint 1
Every AWS list API is paged, and the page size is the service's choice, not yours. One list_objects_v2 call returns at most one page and then quietly tells you, in a field you did not read, that there is more. Nothing raises. You get a dict, you get Contents, your loop runs — and your report is missing three quarters of the bucket. Turning MaxKeys up does not fix it: S3 clamps it and hands you the same page back.
### Hint 2
boto3 already knows how to do this. Ask the client for a paginator with s3.get_paginator("list_objects_v2"), then call .paginate(Bucket=...) on it. That gives you an iterable of response dicts, one per page, with the continuation token threaded through for you. Two loops: pages on the outside, page.get("Contents", []) on the inside. Accumulate as you go.
### Hint 3
Different data — every IAM user in an account, same shape:

```python
pager = iam.get_paginator('list_users')
names, oldest = [], None
for page in pager.paginate():
    for user in page.get('Users', []):
        names.append(user['UserName'])
        if oldest is None or user['CreateDate'] < oldest:
            oldest = user['CreateDate']
print(len(names), oldest)
```

The operation name changes and the field names change; the two loops and the running total do not. Yours adds up Size instead of tracking a date.
