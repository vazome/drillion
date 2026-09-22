---
title: "range over a list: one object per entry, and $ to reach the release"
difficulty: hard
minutes: 20
prereqs: [285, 287]
track: helm
tags: [templates, range, service]
kind: helm
edits: templates/services.yaml
---
# range over a list: one object per entry, and $ to reach the release

*A chart should not need editing to get a third Service. Put the Services in a list in the values, loop over it, and the template writes as many as the list holds.*

## Read first
- [Flow Control: Looping with range](https://helm.sh/docs/chart_template_guide/control_structures/#looping-with-the-range-action): `range`, and what `.` becomes inside it
- [Variables](https://helm.sh/docs/chart_template_guide/variables/): `$`, the root scope that never changes

## Why
A gateway listens on several ports: traffic on one, an admin page on another, metrics on a third. Each wants its own Service, and different installs want different sets. Writing each Service into the chart means a chart change every time a listener is added.

`range` loops over a list in the values and renders its body once per entry, so the values decide how many objects there are. Two things make the loop harder than it looks.

The first is `.`. Inside `range`, the dot is no longer the whole chart context: it is the current entry. `.name` and `.port` read the entry, which is what you want, and `.Release.Name` tries to read a key called `Release` from the entry and fails. The chart context is still there under `$`, which always means the root, so the release name inside a loop is `$.Release.Name`.

The second is the file. One template file may render several objects, but YAML needs a `---` line between them, so the separator goes inside the loop, before each object.

## You get
The chart with `templates/services.yaml` missing, and its `values.yaml` in a tab with two listeners. Run renders your template; Submit renders it twice, with lists of different lengths, and grades both.

## You return
`templates/services.yaml`: one Service per entry in `listeners`, in the order the list gives them.

## Rules
- one Service per listener, and nothing else in the file
- each Service is named after the release and the listener's `name`, joined with a dash
- each selects the pods labelled `app` with the release name
- each has exactly one port: `port` and `targetPort` both the listener's `port`
- nothing about the list may be typed in: the second render uses a different one

## Hints
### Hint 1
The loop is `range`, the list, the body, and `end`. The body is a whole Service, with `---` as its first line:

```yaml
{{- range .Values.listeners }}
---
apiVersion: v1
kind: Service
...
{{- end }}
```

### Hint 2
Inside the loop, the entry's fields are `.name` and `.port`. Try `{{ .Release.Name }}` there once and Run, to see the error Helm gives for it.

### Hint 3
The release through `$`, and the entry through `.`, side by side:

```yaml
metadata:
  name: {{ $.Release.Name }}-{{ .name }}
```
