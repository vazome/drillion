---
title: "a ConfigMap from a map: range, and why every value gets quote"
difficulty: medium
minutes: 15
prereqs: [270, 284]
track: helm
tags: [templates, configmap, range]
kind: helm
edits: templates/configmap.yaml
---
# a ConfigMap from a map: range, and why every value gets quote

*When the chart does not know the keys in advance, the template cannot name them. It has to walk whatever it is given.*

## Read first
- [Flow control: looping with range](https://helm.sh/docs/chart_template_guide/control_structures/#looping-with-the-range-action): how a template walks a map
- [Template functions](https://helm.sh/docs/chart_template_guide/function_list/#quote): `quote`, and why a pipeline reads left to right

## Why
Settings charts take a map of configuration and turn every entry into one key of a ConfigMap. The chart author cannot know which keys an installer will pass, so the template cannot spell them out. It loops.

A loop over a map hands you each key and each value in turn, and inside the loop you write one line of YAML per entry. That is the first half of this task.

The second half is the value. A ConfigMap holds strings and nothing else. `100` and `true` in `values.yaml` arrive as a number and a boolean, and written straight into the manifest they stay a number and a boolean, which the Kubernetes schema refuses. Quoting every value on its way out is the habit that makes the loop safe for any map.

## You get
The chart with `templates/configmap.yaml` missing, and its `values.yaml` open in a tab. Run renders your template with those values. Submit renders it twice, and the second render passes a map with different keys.

## You return
`templates/configmap.yaml`: a ConfigMap named after the release with `-config` on the end, holding one key per entry of the `config` value, each value as a string.

## Rules
- the name is the release name followed by `-config`
- every entry of `config` becomes one key under `data`, spelled as it is in the values, and there are no other keys
- every value is written as a string, whatever type it had in the values
- the keys are not typed into the template: the second render uses different ones

## Hints
### Hint 1
A loop over a map gives you two variables per turn:

```yaml
{{- range $key, $value := .Values.config }}
...
{{- end }}
```

Whatever you write between the two lines appears once per entry.

### Hint 2
One line per entry, indented to sit under `data:`, with the value piped through `quote`:

```yaml
data:
  {{- range $key, $value := .Values.config }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
```

The dashes inside the braces eat the whitespace before them, which is what keeps blank lines out of the render. Run it, and look for any line under `data:` whose value has no quotes.

### Hint 3
The same loop, building a list instead of a map. Given

```yaml
hosts:
  - shop.example.com
  - www.shop.example.com
```

a template writes one rule per host with

```yaml
rules:
  {{- range .Values.hosts }}
  - host: {{ . | quote }}
  {{- end }}
```

Over a list, `range` with no variables sets `.` to each item in turn. Over a map, name the key and the value and use both.
