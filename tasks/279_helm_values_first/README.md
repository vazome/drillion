---
title: install a chart with your own values.yaml
difficulty: easy
minutes: 12
prereqs: [268, 272]
track: helm
tags: [helm, values, deployment, service]
kind: helm
edits: values.yaml
---
# install a chart with your own values.yaml

*Nobody writes a chart the first time they meet Helm. They install someone else's, and everything they get to say about it goes in one file.*

## Read first
- [Values files](https://helm.sh/docs/chart_template_guide/values_files/): where values come from and which one wins
- [Schema files](https://helm.sh/docs/topics/charts/#schema-files): what `values.schema.json` checks before anything renders

## Why
A Helm chart is a folder of Kubernetes manifests with holes in them. The holes read from `.Values`, and `values.yaml` is what fills them. Installing a chart well means reading its templates, finding the value each hole reads, and writing exactly that key, at exactly that depth, with exactly that type.

This chart is the Deployment and the Service you already wrote by hand, with the parts that change between installs turned into values. The templates are open in the tabs above the editor. They are read-only: the chart belongs to someone else, and your say in it is `values.yaml`.

The chart also ships a `values.schema.json`. Helm checks your values against it before it renders anything, so a misspelt key or a number where a string belongs is refused with the path that is wrong. Good charts have one. Many do not, and a later task shows what that costs.

## You get
A chart with no `values.yaml`, and the requirements below. Run renders the chart with your values and shows you the manifests it produced. Submit grades those manifests.

## You return
A `values.yaml` that makes the chart run `{replicas}` replicas of `{image}` and serve them on port `{port}`.

## Rules
- the chart is installed as the release `{release}`; the release name is not a value, and you do not set it
- every key goes where the templates read it, spelled the way they spell it
- the image is two values, the repository and the tag, and the chart joins them with a colon
- the tag is a string. `1.27` without quotes is a number to YAML, and the schema refuses it
- the port and the replica count are numbers, so they carry no quotes

## Hints
### Hint 1
Open `templates/deployment.yaml` and look for `.Values`. Every `.Values.x.y` is a key `x` with a key `y` under it in your file. There are four of them across the two templates, and the schema tab lists the same four as required.

### Hint 2
The depth in the template is the indentation in your file. `.Values.image.repository` is:

```yaml
image:
  repository: ...
```

and `.Values.replicaCount` sits at the top level on its own. Split the image at the colon: the part before it is the repository, the part after it is the tag, and the tag gets quotes.

### Hint 3
The same reading on a different chart. If a template says

```yaml
replicas: {{ .Values.workers.count }}
image: "{{ .Values.worker.image }}"
```

then the values that fill it are

```yaml
workers:
  count: 4
worker:
  image: "busybox:1.36"
```

Two top-level keys, because the template reads two different parents. The spelling is the template's, never your guess at it: `worker` and `workers` are different keys, and only the schema, when there is one, will tell you which one you missed.
