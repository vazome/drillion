---
title: a checksum annotation, so a config change rolls the pods
difficulty: medium
minutes: 20
prereqs: [315, 305]
track: helm
tags: [helm, templates, configmap, rollout, annotations]
kind: helm
edits: templates/deployment.yaml
---
# a checksum annotation, so a config change rolls the pods

*Change a value in a ConfigMap, run `helm upgrade`, and nothing happens: the pods read their environment when they started, and nothing told them to start again.*

## Read first
- [Automatically Roll Deployments](https://helm.sh/docs/howto/charts_tips_and_tricks/#automatically-roll-deployments): the `sha256sum` annotation, from Helm's own tips
- [Deployments: updating](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#updating-a-deployment): only a change to the pod template starts a rollout

## Why
A Deployment rolls out new pods when its pod template changes, and at no other time. A ConfigMap is a separate object. Upgrade a release with a new log level and Helm updates the ConfigMap, leaves the Deployment exactly as it was, and every running pod keeps the environment it started with. The change is applied and has no effect, which is worse than failing.

The fix every mature chart uses is an annotation on the pod template holding a checksum of the ConfigMap. Helm renders the ConfigMap's template, hashes the text, and writes the hash into the Deployment. Change any value that reaches the ConfigMap, and the hash changes, the pod template changes with it, and the Deployment rolls its pods in the normal, gradual way. Change nothing, and the hash stays the same and nothing restarts.

Two details decide whether it works. The annotation has to be on the pod template, `spec.template.metadata`, because that is what a Deployment compares. And the checksum has to be taken over the rendered ConfigMap, the one with this release's values in it, not over the file as it sits in the chart, which never changes between upgrades.

## You get
The chart with `templates/deployment.yaml` missing. Its ConfigMap template and `values.yaml` are in the tabs above. Run renders the chart; Submit renders it twice, with two different configs, and checks the hash each time.

## You return
`templates/deployment.yaml`: a Deployment for the release whose pods take their environment from the ConfigMap, and roll whenever the ConfigMap's rendered content changes.

## Rules
- the Deployment is named after the release, and its selector and pod template both carry `app` set to the release name
- one container, running the image repository and tag from the values, reading its environment from the ConfigMap `<release>-config` with `envFrom`
- the pod template has an annotation `checksum/config`: the sha256 of the rendered `templates/configmap.yaml`

## Hints
### Hint 1
`envFrom` turns every key of a ConfigMap into an environment variable at once:

```yaml
          envFrom:
            - configMapRef:
                name: {{ .Release.Name }}-config
```

### Hint 2
Annotations sit beside labels, under the pod template's `metadata`:

```yaml
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
      annotations:
        checksum/config: ...
```

### Hint 3
`include` renders a template by name, and every file in `templates/` is also a template named after its path. `$.Template.BasePath` is that path's `templates` directory, so `print` builds the name and `sha256sum` hashes what comes back:

```yaml
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```
