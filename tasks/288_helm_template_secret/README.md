---
title: "a Secret from values: pipelines, b64enc and quote"
difficulty: medium
minutes: 12
prereqs: [271, 284]
track: helm
tags: [templates, secret, base64]
kind: helm
edits: templates/secret.yaml
---
# a Secret from values: pipelines, b64enc and quote

*A value on its way into a manifest can pass through several functions, left to right, and the order is the whole point.*

## Read first
- [Template functions and pipelines](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/): how a value flows through functions in order
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/): `data` holds base64, `stringData` holds plain text

## Why
In task 271 you wrote a Secret with `stringData` and let the API server do the encoding. Charts usually write `data` instead, which means the template has to encode each value itself. That is a pipeline: take the value, base64 encode it, then quote the result so YAML reads it as a string.

The order matters. Encoding and then quoting gives a quoted base64 string, which is what Kubernetes wants. Quoting first would encode the quote marks as part of the password. Leaving the encoding out gives plain text in a field that must hold base64, and Kubernetes would read it as garbage bytes, or refuse it.

A pipeline is read left to right: the value on the left is handed to the function on its right, and the result to the next one. It is the same idea as a shell pipe, and it is how most template lines in real charts are written.

## You get
The chart with `templates/secret.yaml` missing, and its `values.yaml` open in a tab. Submit renders it twice, with different credentials, and decodes what you rendered.

## You return
`templates/secret.yaml`: an Opaque Secret named after the release with `-auth` on the end, holding the username and the password from the values under `data`, base64 encoded.

## Rules
- the name is the release name followed by `-auth`
- `type: Opaque`
- the two keys are `username` and `password`, under `data`, not `stringData`
- each value is encoded by the template, then quoted
- no credential is typed into the template: the second render uses different ones

## Hints
### Hint 1
Each line under `data` is one value from the values, passed through two functions. `b64enc` encodes, `quote` wraps the result in quotes, and the pipe `|` hands a value from left to right.

### Hint 2
The shape of one line:

```yaml
data:
  username: {{ .Values.auth.username | b64enc | quote }}
```

and the same for the password. Run it, and decode what you see: `echo <value> | base64 -d` in a terminal gives back the text you started with.

### Hint 3
The same pipeline, with a different first step. A chart that stores a connection string builds it first and encodes the result:

```yaml
data:
  url: {{ printf "postgres://%s@db:5432/app" .Values.auth.username | b64enc | quote }}
```

`printf` makes the string, `b64enc` encodes all of it, `quote` wraps it. Each function gets exactly what the one before it produced, so a mistake in the order shows up in the decoded text, not as an error.
