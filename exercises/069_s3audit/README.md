---
title: boto3 task — audit S3 buckets for public access
minutes: 25
prereqs: [68]
tags: [cloud, boto3]
practices: [30, 43, 68]
---
# boto3 task — audit S3 buckets for public access

*The bucket that leaked was never meant to be public; nobody ever looked.*

## Why
A security review asks: "which of our storage buckets can anyone on
the internet read?" Data leaks usually come from a bucket that was never
meant to be public and that nobody checked. A bucket can be opened two
separate ways: an access-control list (ACL, a list of who may do what)
that grants everyone read, or an attached policy document that allows
everyone. Both must be checked on every bucket, because a script that
checks one and stops reports "all clear" on a bucket the world is
reading. You produce the list of exposed bucket names.

## You get
`s3` — an AWS S3 client object. The test hands in one connected
to a fake in-memory AWS (moto) pre-loaded with a mix of private and
exposed buckets; nothing real is contacted. You are not told the bucket
names; you ask the client for them.

## You return
a sorted list of the names of buckets open to the whole
internet, with no duplicates; an empty list if none are.

## Rules
Find every bucket in the account that anyone on the internet can read.

`s3` is a boto3 S3 client. You are not told which buckets exist — start
from `s3.list_buckets()`, whose answer holds "Buckets", a list of dicts
each with a "Name". A bucket can be exposed two different ways and you
have to check both.

1. Its ACL. `s3.get_bucket_acl(Bucket=name)` answers with "Grants", a
   list of dicts shaped {"Grantee": {...}, "Permission": "READ"}. It is
   public when some grantee has

```
Grantee["URI"] == "http://acs.amazonaws.com/groups/global/AllUsers"
```

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

```
exc.response["Error"]["Code"]     # "NoSuchBucketPolicy"
```

   Catch that one and move on. Let anything else through.

Return the sorted list of exposed bucket names, no duplicates:

```
["acme-static-site-441", "globex-backups-207"]
```

Return [] when the account is clean. `json` and `ClientError` are already
imported at the top of this file. Read only — do not change any bucket.

## Hints
### Hint 1
Two independent doors into the same bucket, so a script that checks one and stops is a script that reports 'all clear' on a bucket the world is reading. Beyond that, the shape of the answers is the whole difficulty: the ACL grants are dicts that mostly do not have the key you want to compare, and the policy comes back as text rather than as parsed JSON. And absence is signalled by an exception, not by an empty result — a bucket with no policy blows up the loop on the first private bucket.
### Hint 2
One loop over list_buckets()["Buckets"], and for each name two checks. For the ACL: any() over get_bucket_acl(...)['Grants'] testing grant['Grantee'].get('URI') against the AllUsers string — .get, not [], because the owner grant has no URI. For the policy: wrap the get_bucket_policy call in try/except ClientError, re-raise unless exc.response['Error']['Code'] is 'NoSuchBucketPolicy', then json.loads(resp['Policy']) and loop the statements. Collect names in a list, and return sorted() of it.
### Hint 3
Different data — the same three moves against IAM, where the risky thing is a role any account can assume:

```python
risky = []
for role in iam.list_roles()['Roles']:
    doc = role['AssumeRolePolicyDocument']
    for stmt in doc['Statement']:
        who = stmt.get('Principal')
        if stmt['Effect'] == 'Allow' and who in ('*', {'AWS': '*'}):
            risky.append(role['RoleName'])
            break
print(sorted(risky))
```

The break matters: one matching statement is enough, and without it a role with two open statements lands in the list twice. Yours does this over parsed bucket policies, plus the ACL check, plus the try/except.
