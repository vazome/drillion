---
title: "include and nindent: a helper's lines, at the depth YAML wants"
difficulty: medium
minutes: 15
prereqs: [314]
track: helm
tags: [templates, named-templates, indentation]
kind: helm
edits: templates/deployment.yaml
---
# include and nindent: a helper's lines, at the depth YAML wants

*A helper's output is text with no idea where it is going. In YAML, where it goes is decided by its indentation, and getting that right is most of calling a helper.*

## Read first
- [The include function](https://helm.sh/docs/chart_template_guide/named_templates/#the-include-function): why charts call helpers with `include`, not `template`
- [Template functions: nindent](https://helm.sh/docs/chart_template_guide/function_list/#nindent): a newline, then every line indented

## Why
In 314 you wrote the helpers. This is the other side: a Deployment that uses a chart's helpers instead of spelling out its own names and labels. It is the file you will write most often, because every new object in a chart starts by calling the same three.

Helpers are called with `include`, which returns the helper's text so that it can be piped into another function. The older `template` action writes the text straight out, and cannot be piped, which is why no modern chart uses it.

What the text is piped into is `nindent`. A helper returns its lines flush left, and YAML reads indentation as structure: labels under `metadata` sit four spaces in, under `spec.selector.matchLabels` six, under the pod template's labels eight. `nindent 4` starts a new line and indents every line of the helper by four. With a dash at the start of the tag, which trims the whitespace before it, the helper lands exactly where a hand-written block would. Get the number wrong and the labels become children of the wrong key, or break the YAML altogether.

## You get
The chart with `templates/deployment.yaml` missing. Its `_helpers.tpl` and `values.yaml` are in the tabs above. Run renders your template; Submit renders it twice, as two releases with two sets of values, and grades both.

## You return
`templates/deployment.yaml`: a Deployment named and labelled entirely by the chart's helpers, with its replica count, image and port read from the values.

## Rules
- the Deployment's name is `api.fullname`
- its `metadata.labels` is `api.labels`
- its `spec.selector.matchLabels` and its pod template's labels are both `api.selectorLabels`
- call each helper with `include`, and indent it with `nindent`
- one container; its replica count, image repository and tag, and `containerPort` come from the values

## Hints
### Hint 1
A helper that returns one short string, like the name, goes inline with no indentation at all:

```yaml
metadata:
  name: {{ include "api.fullname" . }}
```

### Hint 2
A helper that returns several lines goes on the line of the key it belongs under, piped through `nindent` with the depth of its first line. Count the spaces before the key, add two:

```yaml
metadata:
  name: {{ include "api.fullname" . }}
  labels:
    {{- include "api.labels" . | nindent 4 }}
```

### Hint 3
The selector is two levels deeper than `metadata.labels`, and the pod template's labels two deeper again:

```yaml
spec:
  selector:
    matchLabels:
      {{- include "api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "api.selectorLabels" . | nindent 8 }}
```
