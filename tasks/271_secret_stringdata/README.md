---
title: a Secret's data is base64, and stringData is the honest way in
difficulty: easy
minutes: 15
track: kubernetes
tags: [kubernetes, secret, base64]
kind: manifest
---
# a Secret's data is base64, and stringData is the honest way in

*A Secret is a ConfigMap that treats its contents as sensitive. The price of that is an encoding step, and the API built a door around it.*

## Why
A Secret holds the credentials a workload needs: API keys, passwords, tokens. It looks exactly like a ConfigMap, `metadata` and a mapping of keys, until you look at what is inside `data`. That field holds base64, because Secrets are stored and passed around in places that are not safe for raw bytes. It is an encoding, and encryption is a different thing entirely: anyone who can read the Secret can decode it.

So there are two ways in. `data` demands you encode the value yourself, and a value that was encoded twice, or forgotten once, arrives broken at the container with nothing pointing at the mistake. `stringData` is the convenience door the API added: you write the plain text, Kubernetes encodes it on the way in. What you write in `stringData` never comes back out of the API that way, which surprises people later; it is a write-only convenience field.

A Secret also carries a `type`, and for keys and passwords of the ordinary kind that is `Opaque`: opaque to the API, meaningful only to whatever reads it. Typed Secrets, like the ones that hold TLS keys or docker registry logins, make the API check their shape. This task asks for the plain one.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Secret: named `{name}`, of type `Opaque`, holding `API_KEY: {value}` written in `stringData`.

## Rules
- one YAML document, one Secret, nothing else in the file
- `apiVersion` is `v1`. A Secret is a core object
- `type` is `Opaque`
- the entry goes under `stringData`, with the value written as plain text and no encoding of your own
- no `data` field at all. Hand-encoding is the next task's problem, and a value that is base64 of base64 is the bug this task exists to prevent

## Hints
### Hint 1
The skeleton of a ConfigMap, plus one field:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ...
type: Opaque
stringData:
  ...
```

`type` sits under the Secret itself, a sibling of `metadata`, and `stringData` sits under `spec`-less `spec`: like a ConfigMap, a Secret has no `spec`.

### Hint 2
The entry is one line, plain text:

```yaml
stringData:
  API_KEY: some-key-from-a-provider
```

If you find yourself typing `=` and ending the value in `=` or `==`, you are encoding. Delete that and write the value the way the provider gave it to you.

### Hint 3
Why the encoding exists at all: `data` values are what the API stores and hands to containers, and they must survive being written into files and URLs where raw bytes break. The same trick appears all over Kubernetes, wherever a field might have to carry bytes: certificates in TLS Secrets, the `data` of a ConfigMap mounted as a file. `stringData` is the write-side door; `data` is what everything reads back.
