def solve(s3):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import contextlib
import json
import os

import boto3
from _lib import rng
from botocore.exceptions import ClientError
from moto import mock_aws

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
    return [(f"{org}-{words[i]}-{r.randint(100, 999)}", kind)
            for i, kind in enumerate(kinds)]


def _statement(effect, principal, bucket):
    return {"Effect": effect, "Principal": principal, "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket}/*"}


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
                    f"{len(truth)} of {len(spec)} buckets are open to the world")
