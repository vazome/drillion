"""Every AWS list call answers with one page; the rest of the account is on page two."""

import contextlib
import os

import boto3
from _lib import rng
from moto import mock_aws

META = {"topic": 68, "title": "boto3 — client vs resource, and paginators",
        "tier": 3, "minutes": 20, "prereqs": [], "tags": ["cloud", "boto3"]}


def solve(s3, bucket):
    """WHY: Finance asks "how much is stored in the logs bucket, and what
    exactly is in it?". AWS answers list requests one page at a time, about
    a thousand entries per page, and only quietly notes that more exist. A
    script that reads one page reports a fraction of the bucket, and nobody
    notices until the bill disagrees with the report. You are asked for the
    full list of object names and the total size, walking every page.

    YOU GET: `s3` — an AWS S3 client object, the thing you call to talk to
    the storage service. The test hands in one connected to a fake
    in-memory AWS (moto), so nothing real is contacted and no money is
    spent.
    `bucket` — a string bucket name like "acme-logs-412". It already exists
    and holds more objects than a single page returns.

    YOU RETURN: a pair (tuple): a sorted list of every object name (strings),
    and the total size in bytes as a whole number.

    ─── exact rules ───
    Report every object in a bucket that is bigger than one page.

    `s3` is a boto3 S3 *client*: a thin skin over the HTTP API where one
    method call is one request and every answer is a plain dict. The other
    flavour, `boto3.resource("s3")`, wraps the same API in objects and hides
    the paging from you. The client is the one interviews ask about, and the
    one where the paging is your problem, so work with it here.

    `bucket` is the name of a bucket that already exists and already holds
    more objects than a single API call will hand back.

    Return the tuple (keys, total_bytes):

      - keys: every object key in the bucket, as a sorted list of strings
      - total_bytes: the sum of every object's Size, as an int

    A bucket holding three objects would give:

        (["logs/a.log", "logs/b.log", "raw/c.json"], 4096)

    The response dict from a list call puts the objects under "Contents", and
    each one is itself a dict with "Key" and "Size" among other fields. A page
    with nothing on it has no "Contents" key at all, so reach for it with
    .get. Asking for a bigger page does not get you the whole bucket — the
    service caps the page size and ignores you. Do not create or delete
    anything.
    """
    raise NotImplementedError


HINTS = [
    ("Every AWS list API is paged, and the page size is the service's choice, "
    "not yours. One list_objects_v2 call returns at most one page and then "
    "quietly tells you, in a field you did not read, that there is more. "
    "Nothing raises. You get a dict, you get Contents, your loop runs — and "
    "your report is missing three quarters of the bucket. Turning MaxKeys up "
    "does not fix it: S3 clamps it and hands you the same page back."),
    ("boto3 already knows how to do this. Ask the client for a paginator with "
    "s3.get_paginator(\"list_objects_v2\"), then call .paginate(Bucket=...) "
    "on it. That gives you an iterable of response dicts, one per page, with "
    "the continuation token threaded through for you. Two loops: pages on the "
    "outside, page.get(\"Contents\", []) on the inside. Accumulate as you go."),
    ("Different data — every IAM user in an account, same shape:\n"
    "    pager = iam.get_paginator('list_users')\n"
    "    names, oldest = [], None\n"
    "    for page in pager.paginate():\n"
    "        for user in page.get('Users', []):\n"
    "            names.append(user['UserName'])\n"
    "            if oldest is None or user['CreateDate'] < oldest:\n"
    "                oldest = user['CreateDate']\n"
    "    print(len(names), oldest)\n"
    "The operation name changes and the field names change; the two loops and "
    "the running total do not. Yours adds up Size instead of tracking a date."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

_FAKE_AWS = {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
             "AWS_SECURITY_TOKEN": "testing", "AWS_SESSION_TOKEN": "testing",
             "AWS_DEFAULT_REGION": "us-east-1"}


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


def _shrink_pages(size):
    """Real S3 returns at most 1000 keys per call whatever MaxKeys you ask for.
    Filling a bucket with 1000+ objects would make this drill slow, so we pin
    every list call to a small page instead. Same cap, same code, less waiting."""
    boto3.DEFAULT_SESSION.events.register(
        "provide-client-params.s3.ListObjectsV2",
        lambda params, **kwargs: params.update(MaxKeys=size))


def _gen(r):
    """Spec for one bucket: name, the page size to pin, and the objects."""
    prefix = r.choice(["logs", "backups", "raw", "artifacts", "exports"])
    ext = r.choice([".log", ".json", ".gz", ".txt"])
    page = r.choice([20, 25, 40, 50])
    # always a few whole pages plus a partial one, so a single call can never
    # be enough and the last page is never empty
    count = page * r.randint(3, 6) + r.randint(1, page - 1)
    bucket = "{}-{}-{}".format(r.choice(["acme", "globex", "initech"]), prefix,
                               r.randint(100, 999))
    objects = [(f"{prefix}/{i:05d}{ext}", r.randint(1, 400))
               for i in range(count)]
    return {"bucket": bucket, "page": page, "objects": objects}


def _build(spec, s3):
    s3.create_bucket(Bucket=spec["bucket"])
    for key, size in spec["objects"]:
        s3.put_object(Bucket=spec["bucket"], Key=key, Body=b"x" * size)


def _reference(s3, bucket):
    keys, total_bytes = [], 0
    pager = s3.get_paginator("list_objects_v2")
    for page in pager.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
            total_bytes += obj["Size"]
    return sorted(keys), total_bytes


def test_solve():
    r = rng()
    previous_session = boto3.DEFAULT_SESSION
    with _fake_aws_env():
        try:
            for _ in range(3):
                spec = _gen(r)
                with mock_aws():
                    boto3.setup_default_session()
                    _shrink_pages(spec["page"])
                    s3 = boto3.client("s3", region_name="us-east-1")
                    _build(spec, s3)

                    truth = (sorted(k for k, _ in spec["objects"]),
                             sum(size for _, size in spec["objects"]))
                    assert _reference(s3, spec["bucket"]) == truth, "fixture drifted"
                    got = solve(s3, spec["bucket"])
                    assert got == truth, (
                        "the bucket holds {} objects across {} pages, "
                        "totalling {} bytes".format(
                            len(truth[0]),
                            -(-len(truth[0]) // spec["page"]), truth[1]))
        finally:
            boto3.DEFAULT_SESSION = previous_session
