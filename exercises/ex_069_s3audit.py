"""The bucket that leaked was never meant to be public; nobody ever looked."""

import contextlib
import json
import os

import boto3
from botocore.exceptions import ClientError
from moto import mock_aws

from _lib import rng

META = {"topic": 69, "title": "boto3 task — audit S3 buckets for public access",
        "tier": 4, "minutes": 25, "prereqs": [68],
        "practices": [30, 43, 68]}


def solve(s3):
    """Find every bucket in the account that anyone on the internet can read.

    `s3` is a boto3 S3 client. You are not told which buckets exist — start
    from `s3.list_buckets()`, whose answer holds "Buckets", a list of dicts
    each with a "Name". A bucket can be exposed two different ways and you
    have to check both.

    1. Its ACL. `s3.get_bucket_acl(Bucket=name)` answers with "Grants", a
       list of dicts shaped {"Grantee": {...}, "Permission": "READ"}. It is
       public when some grantee has

           Grantee["URI"] == "http://acs.amazonaws.com/groups/global/AllUsers"

       Most grantees are the bucket owner and carry no "URI" key at all.
       A grant to .../groups/global/AuthenticatedUsers is a different group
       and does NOT count — that is any AWS customer, not the whole internet.

    2. Its bucket policy. `s3.get_bucket_policy(Bucket=name)` answers with
       "Policy", which is a JSON **string**, not a dict. Parse it and look at
       its "Statement" list. It is public when some statement has both
       "Effect": "Allow" and a "Principal" of either the bare string "*" or
       the dict {"AWS": "*"}. A statement naming a real account is not
       public, and neither is "Effect": "Deny" — even with Principal "*".
       A statement list can be longer than one, so check all of them.

       A bucket with no policy at all does not answer with an empty policy.
       It raises botocore.exceptions.ClientError, and the code that tells you
       which failure it was lives at

           exc.response["Error"]["Code"]     # "NoSuchBucketPolicy"

       Catch that one and move on. Let anything else through.

    Return the sorted list of exposed bucket names, no duplicates:

        ["acme-static-site-441", "globex-backups-207"]

    Return [] when the account is clean. `json` and `ClientError` are already
    imported at the top of this file. Read only — do not change any bucket.
    """
    raise NotImplementedError


HINTS = [
    "Two independent doors into the same bucket, so a script that checks one "
    "and stops is a script that reports 'all clear' on a bucket the world is "
    "reading. Beyond that, the shape of the answers is the whole difficulty: "
    "the ACL grants are dicts that mostly do not have the key you want to "
    "compare, and the policy comes back as text rather than as parsed JSON. "
    "And absence is signalled by an exception, not by an empty result — a "
    "bucket with no policy blows up the loop on the first private bucket.",
    "One loop over list_buckets()[\"Buckets\"], and for each name two checks. "
    "For the ACL: any() over get_bucket_acl(...)['Grants'] testing "
    "grant['Grantee'].get('URI') against the AllUsers string — .get, not [], "
    "because the owner grant has no URI. For the policy: wrap the "
    "get_bucket_policy call in try/except ClientError, re-raise unless "
    "exc.response['Error']['Code'] is 'NoSuchBucketPolicy', then "
    "json.loads(resp['Policy']) and loop the statements. Collect names in a "
    "list, and return sorted() of it.",
    "Different data — the same three moves against IAM, where the risky thing "
    "is a role any account can assume:\n"
    "    risky = []\n"
    "    for role in iam.list_roles()['Roles']:\n"
    "        doc = role['AssumeRolePolicyDocument']\n"
    "        for stmt in doc['Statement']:\n"
    "            who = stmt.get('Principal')\n"
    "            if stmt['Effect'] == 'Allow' and who in ('*', {'AWS': '*'}):\n"
    "                risky.append(role['RoleName'])\n"
    "                break\n"
    "    print(sorted(risky))\n"
    "The break matters: one matching statement is enough, and without it a "
    "role with two open statements lands in the list twice. Yours does this "
    "over parsed bucket policies, plus the ACL check, plus the try/except.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

_FAKE_AWS = {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
             "AWS_SECURITY_TOKEN": "testing", "AWS_SESSION_TOKEN": "testing",
             "AWS_DEFAULT_REGION": "us-east-1"}

_ALL_USERS = "http://acs.amazonaws.com/groups/global/AllUsers"

# kind -> is it actually exposed. Every one of these is built at least once.
_KINDS = {
    "private": False,          # nothing set
    "acl_public": True,        # AllUsers READ grant, no policy
    "acl_auth": False,         # AuthenticatedUsers grant — not the internet
    "policy_open": True,       # single Allow / Principal *
    "policy_open_second": True,   # Allow * hiding behind a harmless statement
    "policy_deny": False,      # Deny with Principal * — the safe direction
    "policy_account": False,   # Allow, but to one named account
    "both": True,              # public ACL and open policy at once
}


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
    """Spec: [(bucket_name, kind), ...]. Every kind appears at least once."""
    kinds = list(_KINDS)
    kinds += [r.choice(kinds) for _ in range(r.randint(0, 4))]
    r.shuffle(kinds)
    org = r.choice(["acme", "globex", "initech", "hooli"])
    words = ["backups", "static-site", "logs", "reports", "uploads", "tfstate",
             "media", "invoices", "raw", "snapshots", "dumps", "cache",
             "exports", "archive", "assets", "audit"]
    r.shuffle(words)
    return [("{}-{}-{}".format(org, words[i], r.randint(100, 999)), kind)
            for i, kind in enumerate(kinds)]


def _statement(effect, principal, bucket):
    return {"Effect": effect, "Principal": principal, "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::{}/*".format(bucket)}


def _build(spec, s3, r):
    """Materialise the buckets. Returns the sorted names that really are open."""
    exposed = []
    for name, kind in spec:
        acl = {"acl_public": "public-read", "acl_auth": "authenticated-read",
               "both": "public-read"}.get(kind)
        s3.create_bucket(Bucket=name, **({"ACL": acl} if acl else {}))

        star = r.choice(["*", {"AWS": "*"}])
        account = {"AWS": "arn:aws:iam::123456789012:root"}
        statements = {
            "policy_open": [_statement("Allow", star, name)],
            "policy_open_second": [_statement("Allow", account, name),
                                   _statement("Allow", star, name)],
            "policy_deny": [_statement("Deny", star, name)],
            "policy_account": [_statement("Allow", account, name)],
            "both": [_statement("Allow", star, name)],
        }.get(kind)
        if statements:
            s3.put_bucket_policy(Bucket=name, Policy=json.dumps(
                {"Version": "2012-10-17", "Statement": statements}))

        if _KINDS[kind]:
            exposed.append(name)
    return sorted(exposed)


def _reference(s3):
    exposed = []
    for bucket in s3.list_buckets()["Buckets"]:
        name = bucket["Name"]
        grants = s3.get_bucket_acl(Bucket=name)["Grants"]
        if any(g["Grantee"].get("URI") == _ALL_USERS for g in grants):
            exposed.append(name)
            continue
        try:
            raw = s3.get_bucket_policy(Bucket=name)["Policy"]
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "NoSuchBucketPolicy":
                raise
            continue
        for stmt in json.loads(raw)["Statement"]:
            who = stmt.get("Principal")
            if stmt["Effect"] == "Allow" and who in ("*", {"AWS": "*"}):
                exposed.append(name)
                break
    return sorted(exposed)


def test_solve():
    r = rng()
    with _fake_aws_env():
        for _ in range(3):
            spec = _gen(r)
            with mock_aws():
                s3 = boto3.client("s3", region_name="us-east-1")
                truth = _build(spec, s3, r)
                assert _reference(s3) == truth, "fixture drifted"
                assert solve(s3) == truth, (
                    "{} of {} buckets are open to the world".format(
                        len(truth), len(spec)))
