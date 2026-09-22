---
title: "blocks from values: toYaml, nindent, and a with that renders nothing"
difficulty: hard
minutes: 20
prereqs: [281, 284]
track: helm
tags: [helm, templates, toyaml, indentation]
kind: helm
edits: templates/deployment.yaml
---
# blocks from values: toYaml, nindent, and a with that renders nothing

*Pasting a block of YAML into another is where templates break. Not with an error, but with a manifest nested one level wrong.*

## Read first
- [Template functions](https://helm.sh/docs/chart_template_guide/function_list/#toyaml): `toYaml`, `indent` and `nindent`
- [Modifying scope using with](https://helm.sh/docs/chart_template_guide/control_structures/#modifying-scope-using-with): a block that only renders when its value has something in it

## Why
In task 281 you filled in a chart that copied `resources` into the container whole. Now you write that chart. The move is short to type and easy to get wrong: turn a value back into YAML, then indent every line of it to exactly the depth of the key it belongs under.

Get the depth wrong by two spaces and the block is still valid YAML. It just belongs to the wrong parent: the requests end up beside the container's name instead of under `resources`, and the file renders without complaint. Kubernetes' schema is what catches it, reporting a field that does not belong where it landed. That is why `nindent`, which starts a fresh line and then indents, is the version people reach for: the depth is written once, as a number, where you can count it.

The node selector adds the other half of pasting a block: when the value is empty, the key should not render at all. An empty node selector rendered as a key with an empty map is legal but it is noise, and a block like `affinity` rendered empty is worse. `with` renders its body only when the value is not empty, and inside it the value is the dot.

## You get
The chart with `templates/deployment.yaml` missing, and its `values.yaml` open in a tab. Submit renders it twice: once with a node selector and a full resources block, once with an empty node selector and a smaller block.

## You return
`templates/deployment.yaml`: one Deployment named after the release, labelled `app` with the release name on both sides, running the image from the values, with the container's resources and the pod's node selector copied from the values as they are.

## Rules
- one replica, one container
- `resources` goes under the container and holds exactly what the values hold
- `nodeSelector` goes under the pod spec, beside `containers`, and holds exactly what the values hold
- when the node selector is empty, the pod spec has no `nodeSelector` key at all
- the name, the labels and the image follow the release and the values

## Hints
### Hint 1
Two blocks, two depths. Count the spaces before `resources:` in your container and before `containers:` in the pod spec. The pasted block has to start two further in than the key it sits under.

### Hint 2
`toYaml` turns the value into YAML text; `nindent N` puts it on a new line with N spaces before every line:

```yaml
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

For the node selector, wrap the key and its block in `with`, so an empty value renders neither, and use `.` inside it for the value.

### Hint 3
The same shape for a different block. Tolerations are a list under the pod spec:

```yaml
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

The dash in `{{-` removes the newline and spaces before the tag, which is why `nindent` then has to add a newline back. `indent` does not, and that single character is the usual source of a block that renders on the same line as its key.
