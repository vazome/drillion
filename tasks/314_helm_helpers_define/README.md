---
title: "_helpers.tpl: name and label a release once, use it everywhere"
difficulty: medium
minutes: 20
prereqs: [284]
track: helm
tags: [templates, named-templates, labels]
kind: helm
edits: templates/_helpers.tpl
---
# _helpers.tpl: name and label a release once, use it everywhere

*Open any real chart and the first file worth reading is `_helpers.tpl`. It is where the chart decides, once, what its objects are called and how they are labelled.*

## Read first
- [Named Templates](https://helm.sh/docs/chart_template_guide/named_templates/): `define`, `include`, and why files starting with `_` are not rendered
- [Labels and Annotations](https://helm.sh/docs/chart_best_practices/labels/): the standard labels a chart puts on everything

## Why
A chart with a Deployment, a Service and a ConfigMap names and labels each of them. Written out in every file, the same five lines drift: someone adds a label to the Deployment and forgets the Service, and the Service's selector quietly stops matching anything.

A named template is a piece of text with a name, defined once and pulled in wherever it is needed. By convention they live in `templates/_helpers.tpl`. Helm renders every file in `templates/` as a manifest except the ones whose names start with an underscore, so the helpers are available to every template without producing an object of their own.

Charts made with `helm create` all carry the same three helpers, and the ones in this task follow them. A full name, the release and the chart joined with a dash, so two installs never collide. Selector labels, the two that pick out this release's pods and must never change once installed, because a Deployment's selector cannot be edited. And the full label set: the selector labels plus the chart's version and the tool that manages it, for everything else to read.

Name every define with the chart's name as a prefix. Named templates are global across a chart and its subcharts, and two charts that both define `fullname` overwrite each other.

## You get
The chart with `templates/_helpers.tpl` missing. Its Deployment and Service already call the three helpers; open them in the tabs above to see how. Run renders the chart; Submit renders it twice, as two different releases, and grades both.

## You return
`templates/_helpers.tpl`, defining the three named templates the chart calls: `web.fullname`, `web.selectorLabels` and `web.labels`.

## Rules
- `web.fullname` is the release name, a dash, and the chart name
- `web.selectorLabels` is exactly two labels: `app.kubernetes.io/name` set to the chart name, and `app.kubernetes.io/instance` set to the release name
- `web.labels` is those two, plus `helm.sh/chart` set to the chart name and version joined with a dash, and `app.kubernetes.io/managed-by` set to the release service
- read the release name from the built-in objects, never type it in: the second render uses a different release

## Hints
### Hint 1
A named template is `define`, a name, the text, and `end`. The dashes trim the newlines on either side, so what comes out is only the text:

```yaml
{{- define "web.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}
```

The built-in objects you need are `.Release.Name`, `.Release.Service`, `.Chart.Name` and `.Chart.Version`.

### Hint 2
A helper that produces several lines writes them flush left, one `key: value` per line. The caller indents them: the Deployment's tab says `include "web.labels" . | nindent 4`.

```yaml
{{- define "web.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Hint 3
One helper can call another, so the full set does not repeat the selector labels. `include` takes the name and the context to render it with, and the context is `.`, the whole of what this template can see:

```yaml
{{- define "web.labels" -}}
{{ include "web.selectorLabels" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```
