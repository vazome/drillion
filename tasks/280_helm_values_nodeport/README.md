---
title: "a NodePort through values: when a value only counts if another says so"
difficulty: easy
minutes: 12
prereqs: [273, 279]
track: helm
tags: [helm, values, service, nodeport]
kind: helm
edits: values.yaml
---
# a NodePort through values: when a value only counts if another says so

*Some values are read only under a condition. Set one without the other and the chart renders happily, and ignores you.*

## Read first
- [Flow control](https://helm.sh/docs/chart_template_guide/control_structures/): `if` and `with` in a template, which decide whether a block renders at all
- [Service type NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport): what the fixed port on every node is for

## Why
Charts expose choices, not only numbers. This one can put its Service on a cluster IP, where only the cluster reaches it, or on a NodePort, where every node listens on a port you pick. The choice is one value, and the port it opens is another.

Read `templates/service.yaml` closely. The node port is written only inside an `if` on the service type, and only when a node port was given at all. Set the port and forget the type, and the chart renders a ClusterIP Service with no node port in it. Nothing fails. That is the thing to learn to look for: a value that is only read when another value lets it be.

## You get
The chart in the tabs above, with no `values.yaml`. Run shows you the manifests your values produce.

## You return
A `values.yaml` that runs `{replicas}` replicas of `{image}`, behind a NodePort Service on port `{port}`, with the node port fixed at `{node_port}`.

## Rules
- the chart is installed as the release `{release}`; you do not set the release name
- every key goes where the templates read it; the schema tab lists them and refuses any other
- the service type is one of the two words the schema allows, spelled as it spells them
- the tag is a string and gets quotes; the ports and the replica count are numbers and do not
- a node port lives between 30000 and 32767, and the schema holds you to it

## Hints
### Hint 1
Start from what task 279 needed: the replica count, the image as repository and tag, and a service port. This chart reads two more keys under `service`. Find them in `templates/service.yaml`.

### Hint 2
Both new keys sit beside `port`:

```yaml
service:
  type: ...
  port: ...
  nodePort: ...
```

`type` has to say `NodePort` exactly, or the `if` around `nodePort` never opens and your node port is silently dropped. Run it, and look at the rendered Service: `type: NodePort` and a `nodePort:` line under the port are the two things to see.

### Hint 3
The same condition on a different chart. A template that reads

```yaml
{{- if .Values.metrics.enabled }}
  - port: {{ .Values.metrics.port }}
{{- end }}
```

needs both of

```yaml
metrics:
  enabled: true
  port: 9102
```

Set only `port`, and the rendered manifest has no metrics port at all: Helm never looks at a value inside an `if` that stayed shut. Whenever a value seems to do nothing, look for the condition around it.
