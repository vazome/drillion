---
title: requests and limits as a nested value the chart copies whole
difficulty: medium
minutes: 14
prereqs: [279]
track: helm
tags: [helm, values, resources, toyaml]
kind: helm
edits: values.yaml
---
# requests and limits as a nested value the chart copies whole

*Some values are not a hole for one number. They are a whole block of Kubernetes, handed over as it is.*

## Read first
- [Resource management for pods](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/): what requests and limits mean, and how quantities are written
- [Template functions](https://helm.sh/docs/chart_template_guide/function_list/#toyaml): `toYaml`, which turns a value back into YAML

## Why
Most charts do not template `resources` field by field. They take a whole mapping from values and paste it under the container with `toYaml`. That makes the chart short and puts the burden on you: whatever you write under `resources` in values arrives in the manifest exactly as written, typos and all.

So the skill here is writing a piece of a Kubernetes manifest inside a values file: the right nesting under `resources`, `requests` and `limits` as siblings, and quantities spelled the way Kubernetes spells them. The schema checks the shape of the block. What it holds is yours.

## You get
The chart in the tabs above, with no `values.yaml`. Run shows the Deployment your values produce.

## You return
A `values.yaml` that runs `{image}` with a request of `{cpu}` CPU and `{memory}` memory, and a memory limit of `{limit_memory}`.

## Rules
- the chart is installed as the release `{release}`; you do not set it
- the image is one string here, repository and tag together, because this chart reads it that way
- the requests and the limit go under `resources`, in the shape a container's `resources` has
- write each quantity exactly as given above, as a string
- set no CPU limit: the task asks for a memory limit only

## Hints
### Hint 1
Look for the `with .Values.resources` block in the template. Everything under `resources` in your values is pasted, indented, under `resources:` in the container. So your values need a `resources` key, and under it exactly what a container's `resources` would hold.

### Hint 2
A container's resources have two siblings, each a mapping:

```yaml
resources:
  requests:
    cpu: ...
    memory: ...
  limits:
    memory: ...
```

Quantities like `250m` and `256Mi` are strings. Run it, and read the rendered container: the block should look exactly like the one you wrote, twelve spaces further in.

### Hint 3
The same pass-through, for a different block. A chart whose template says

```yaml
          {{- with .Values.securityContext }}
          securityContext:
            {{- toYaml . | nindent 12 }}
          {{- end }}
```

takes its values as a piece of a container spec:

```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
```

The chart has no opinion about what is inside. Whatever the Kubernetes field accepts, the values accept, which is why reading the Kubernetes reference is part of filling in a chart.
