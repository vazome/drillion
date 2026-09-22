---
title: "your first template: the Deployment you wrote, with holes in it"
difficulty: medium
minutes: 15
prereqs: [268, 279]
track: helm
tags: [helm, templates, deployment, labels]
kind: helm
edits: templates/deployment.yaml
---
# your first template: the Deployment you wrote, with holes in it

*A chart is a manifest you only write once. Everything that changes between installs becomes a lookup, and everything else stays exactly as you would type it by hand.*

## Read first
- [Getting started with templates](https://helm.sh/docs/chart_template_guide/getting_started/): what a template is, and how Helm renders one
- [Built-in objects](https://helm.sh/docs/chart_template_guide/builtin_objects/): `.Release`, `.Values` and `.Chart`

## Why
In the Kubernetes track you wrote a Deployment by hand: a name, a replica count, an image, and the label that has to agree between the selector and the pod template. Every install of the same service needs that file again with a different name, a different count and a different image. A template is that file written once, with those parts replaced by lookups.

There are two kinds of lookup here. The release name comes from `helm install`, not from values, and it is how two installs of one chart keep their objects apart. The replica count and the image come from `values.yaml`, whose keys are fixed by the chart, so you write the template to read the keys the file in the tab already has.

Everything outside the lookups is plain Kubernetes, and it is checked as plain Kubernetes: the rendered file goes through the same schema your hand-written manifests did.

## You get
The chart with `templates/deployment.yaml` missing, and its `values.yaml` open in a tab. Run renders your template with those values and shows the result. Submit renders it twice, as two different releases with two different sets of values, and grades both.

## You return
`templates/deployment.yaml`: a Deployment whose name, replica count, image and labels come from the release and the values, whatever they are.

## Rules
- the Deployment is named after the release
- the replica count comes from the values, and so do the image's repository and tag, joined with a colon
- the selector and the pod template both carry the label `app`, set to the release name
- one container; its name is yours to choose, and the chart's own name is a good one
- nothing that should follow the release or the values may be typed in: the second render uses different ones

## Hints
### Hint 1
Start from the Deployment you would write by hand, then replace one value at a time with its lookup. The release name is `{{ .Release.Name }}`. A value is `.Values` and then the path to it in `values.yaml`.

### Hint 2
Four lookups, one of them used three times:

```yaml
metadata:
  name: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
```

and the same `{{ .Release.Name }}` under both `selector.matchLabels.app` and the pod template's `labels.app`. The image is two lookups inside one quoted string, with a colon between them.

### Hint 3
The same move on a different object. A hand-written ConfigMap

```yaml
metadata:
  name: shop-settings
data:
  currency: EUR
```

becomes, when the name follows the release and the currency is a value,

```yaml
metadata:
  name: {{ .Release.Name }}-settings
data:
  currency: {{ .Values.currency | quote }}
```

Nothing else changes. The skill is deciding which parts vary between installs, and leaving the rest as plain YAML.
