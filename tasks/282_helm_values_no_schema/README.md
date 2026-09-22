---
title: "a chart with no schema: the typo that renders anyway"
difficulty: medium
minutes: 15
prereqs: [270, 279]
track: helm
tags: [values, env, validation]
kind: helm
edits: values.yaml
---
# a chart with no schema: the typo that renders anyway

*When a chart has defaults and no schema, a misspelt key is not an error. It is a value nobody reads, and the default goes to production instead.*

## Read first
- [Using the default function](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/#using-the-default-function): what a template falls back to when a value is missing
- [Environment variables](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/): `env` as a list of names and values

## Why
Task 279's chart refused a misspelt key before rendering anything, because it shipped a schema. This one does not, and most charts in the wild are like it. Every value here has a default in the template, so the chart always renders, and a key the template never reads is simply ignored. Write `replicas` where it reads `replicaCount` and you get one replica, with no error anywhere.

The defence is the one habit worth keeping for life: after writing values, read the render. Run shows it to you. Check that every number you set is the number you see.

The other half of this task is `env`. Kubernetes wants every environment variable's value as a string, and YAML turns `true` and `3` into a boolean and a number unless they are quoted. The schema that catches that is Kubernetes' own, checked on the render.

## You get
The chart in the tabs above, with no `values.yaml`, and no schema to catch you. Run shows the Deployment your values produce.

## You return
A `values.yaml` that runs `{replicas}` workers on image tag `{tag}`, with `LOG_LEVEL` set to `{log_level}`, `RETRIES` to `{retries}` and `DRY_RUN` to `{dry_run}`.

## Rules
- the chart is installed as the release `{release}`; you do not set it
- every key goes where the template reads it. Nothing will tell you when it does not, except the render
- the three variables go in `env`, as a list of entries with a `name` and a `value`
- every value in `env` is a string, so the numbers and the booleans among them are quoted
- no other environment variables

## Hints
### Hint 1
Find every `.Values` in the template. There are three: one number, one nested string, one list. Anything you write under another name renders nothing and costs you nothing, until you read the output.

### Hint 2
`env` is pasted into the container as it is, so write it the way a container spells it:

```yaml
env:
  - name: SOMETHING
    value: "text"
```

Then quote the values YAML would otherwise read as a number or a boolean. Run, and compare the rendered `replicas:` and `image:` with what you asked for before you compare anything else.

### Hint 3
The silent default, on another chart. Given

```yaml
timeout: {{ .Values.timeoutSeconds | default 30 }}
```

these values

```yaml
timeout: 90
```

render `timeout: 30`, and nothing complains. The key is `timeoutSeconds`. The only place that mistake is visible is the rendered output, which is why `helm template` before `helm install` is a habit and not a formality.
