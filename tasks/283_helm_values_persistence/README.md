---
title: "turn a feature on: a switch, and the values it unlocks"
difficulty: medium
minutes: 14
prereqs: [277, 279]
track: helm
tags: [values, persistentvolumeclaim, toggles]
kind: helm
edits: values.yaml
---
# turn a feature on: a switch, and the values it unlocks

*Half of every real chart is off until you turn it on. The switch is one boolean, and it is the easiest value in the file to get subtly wrong.*

## Read first
- [Flow control](https://helm.sh/docs/chart_template_guide/control_structures/): what counts as true to an `if`
- [PersistentVolumeClaims](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims): the object this switch adds

## Why
Charts ship with optional parts: persistence, an ingress, metrics, a second container. Each one is a block wrapped in `if` on an `enabled` value, and each one brings a few more values that only matter once it is on. Installing one means finding the switch, flipping it, and filling in what it unlocks.

The trap is the switch itself. To a template, the string `"false"` is not empty, so it counts as true, and a quoted `"false"` turns the feature on. This chart's schema only accepts a real boolean, which is why it refuses that. Without a schema you would find out from the render, or from production.

This chart wires one switch to three places: the claim itself, and the volume and the mount in the pod. Turn it on and all three appear together.

## You get
The chart in the tabs above, with no `values.yaml`. Run shows every manifest your values render, and with persistence off that is only the Deployment.

## You return
A `values.yaml` that runs `{image}` with persistence on: a claim of `{size}` on the storage class `{storage_class}`.

## Rules
- the chart is installed as the release `{release}`; you do not set it
- the switch is a boolean: `true`, without quotes
- the size and the storage class sit beside the switch, where the claim's template reads them
- write the size exactly as given; the schema only takes whole numbers of `Mi` or `Gi`

## Hints
### Hint 1
Open `templates/pvc.yaml`. The whole file is inside one `if`. Whatever that `if` reads is the switch, and the two other values the file reads are the ones it unlocks.

### Hint 2
All three live under one key:

```yaml
persistence:
  enabled: true
  size: ...
  storageClass: ...
```

Run it, and count the rendered documents: there should be two now, the Deployment and the claim, and the Deployment should have grown a `volumes` list.

### Hint 3
The same switch on a different chart:

```yaml
{{- if .Values.ingress.enabled }}
...
  host: {{ .Values.ingress.host }}
{{- end }}
```

is filled with

```yaml
ingress:
  enabled: true
  host: shop.example.com
```

and `enabled: "false"` would turn it on, since a non-empty string is true to a template. A boolean switch is always written bare: `true` or `false`.
