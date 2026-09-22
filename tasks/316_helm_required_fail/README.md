---
title: "required and fail: a chart that refuses to install broken"
difficulty: medium
minutes: 15
prereqs: [284]
track: helm
tags: [helm, templates, validation, required, fail]
kind: helm
edits: templates/deployment.yaml
---
# required and fail: a chart that refuses to install broken

*Some values have no safe default. A chart that renders anyway installs something that crashes at startup; a chart that refuses says what is missing before anything reaches the cluster.*

## Read first
- [Template functions: required](https://helm.sh/docs/howto/charts_tips_and_tricks/#using-the-required-function): stop the render when a value is missing
- [Template functions: fail](https://helm.sh/docs/chart_template_guide/function_list/#fail): stop the render with your own message

## Why
A database URL has no default that is right for anyone. Leave it empty in `values.yaml` and install, and the chart renders happily: the pod starts, fails to connect, and restarts until someone reads its logs. The mistake was made at install time, and it is found minutes later, somewhere else.

`required` moves it back to install time. It takes a message and a value, returns the value when it is set, and stops the whole render with the message when it is empty. `helm install` then prints that message and creates nothing.

`fail` is the general form: it stops the render unconditionally, so it goes inside an `if` that decides when a value is set but wrong. The image tag `latest` is the usual example. It is set, and it is also a promise that the next pod restart may run different code from the last, so many teams' charts refuse it outright.

Both messages are read by the person running the install, usually in a hurry. Name the value and say what is wrong with it.

## You get
The chart with `templates/deployment.yaml` missing, and its `values.yaml` in a tab: `database.url` is empty on purpose. Run renders your template with the task's values. Submit renders it four times: twice with good values, which must render, and twice with bad ones, which must be refused.

## You return
`templates/deployment.yaml`: a Deployment for the release that passes `database.url` to its container as `DATABASE_URL`, and refuses to render without one, or with the image tag `latest`.

## Rules
- the Deployment is named after the release, and its selector and pod template both carry `app` set to the release name
- one container, running the image repository and tag from the values, with an environment variable `DATABASE_URL` holding `database.url`
- with `database.url` empty or missing, the render stops with the message `database.url is required`
- with `image.tag` set to `latest`, the render stops with the message `image.tag must be a pinned version, not latest`
- with good values, it renders, and nothing about the refusals shows in the output

## Hints
### Hint 1
`required` wraps the value where it is used. It returns the value, so it can still be piped into `quote`:

```yaml
value: {{ required "database.url is required" .Values.database.url | quote }}
```

### Hint 2
`fail` goes inside an `if`, and the whole block can sit at the top of the file, before `apiVersion`. The dashes keep it from leaving blank lines in the output:

```yaml
{{- if eq .Values.image.tag "latest" }}
{{- fail "image.tag must be a pinned version, not latest" }}
{{- end }}
```

### Hint 3
Each of the four renders is graded on its own, and a failure names which one it was: render 3 has no database URL, render 4 has the tag `latest`. If render 3 says the values rendered, `required` is missing or wraps something other than `.Values.database.url`. If it says Helm's message does not match, compare yours to the rule word for word.
