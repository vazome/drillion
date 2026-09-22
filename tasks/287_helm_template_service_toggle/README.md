---
title: "an optional Service: if around a whole file, and default for a value"
difficulty: medium
minutes: 15
prereqs: [272, 284]
track: helm
tags: [templates, service, toggles]
kind: helm
edits: templates/service.yaml
---
# an optional Service: if around a whole file, and default for a value

*Every optional part of a chart you have ever switched off was written this way: a whole file inside one condition.*

## Read first
- [Flow control](https://helm.sh/docs/chart_template_guide/control_structures/): `if`, and the whitespace dashes that keep a false branch from leaving blank lines
- [Using the default function](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/#using-the-default-function): a value that falls back when it is empty

## Why
In task 283 you turned a chart's feature on from the outside. This is the inside of that switch. A template whose whole body sits in one `if` renders to nothing when the condition is false, and Helm drops the empty file from the output. That is the entire mechanism behind every `enabled: false` you will ever set.

The Service's type shows the other common move. Most installs want ClusterIP and should not have to say so, so the values leave the type empty and the template falls back. `default` takes the value on its right when the value on its left is empty, which covers both an empty string and a key that is not there at all.

The Deployment is already in the chart, and its pods carry `app` set to the release name. The Service has to select them by it.

## You get
The chart with `templates/service.yaml` missing; its `values.yaml` and the Deployment are open in tabs. Submit renders the chart three times: with a type set, with no type, and with the Service switched off.

## You return
`templates/service.yaml`: a Service named after the release, selecting the Deployment's pods, on the port from the values, with the type from the values or ClusterIP when none is given, and nothing at all when the Service is switched off.

## Rules
- the whole Service renders only when `service.enabled` is true
- the type comes from `service.type`, and falls back to ClusterIP when it is empty or missing
- one port: the service port from the values, sent to the container's port 80
- the selector matches the label the pods already carry
- nothing that follows the release or the values is typed in

## Hints
### Hint 1
Write the Service as you would by hand for one install, then wrap the whole file: an `if` on the switch on the first line, and its `end` on the last.

### Hint 2
The frame, and the one line that needs a fallback:

```yaml
{{- if .Values.service.enabled }}
apiVersion: v1
kind: Service
...
spec:
  type: {{ .Values.service.type | default "ClusterIP" }}
...
{{- end }}
```

`.Release.Name` goes in three places: the name, and the selector that has to match the pods' `app` label.

### Hint 3
The same pattern on a different optional object. A chart that can ship a PodDisruptionBudget writes

```yaml
{{- if .Values.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ .Release.Name }}
spec:
  minAvailable: {{ .Values.pdb.minAvailable | default 1 }}
  ...
{{- end }}
```

Switch and fallback together: the file exists only when asked for, and the one number most people will not care about has a sensible value when they leave it out.
