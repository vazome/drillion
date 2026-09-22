---
title: "NodePort: three port fields, and 30000 to 32767 is the law"
difficulty: medium
minutes: 15
prereqs: [272]
track: kubernetes
tags: [service, nodeport]
kind: manifest
---
# NodePort: three port fields, and 30000 to 32767 is the law

*A ClusterIP is reachable from inside the cluster. A NodePort cuts a hole in every node's firewall, and the hole has a legal range.*

## Read first
- [Service](https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport): the NodePort type and the 30000 to 32767 port range

## Why
The default Service answers on a virtual IP that only the cluster can see. Sooner or later somebody outside wants in: a machine in the office, a browser on your laptop. The oldest way is `type: NodePort`: Kubernetes opens one port on every node, and traffic hitting any node on that port is forwarded into the Service you already know.

That makes three port fields on one Service, and keeping them straight is the task. `port` is the inside number, what a cluster client still calls. `targetPort` is the container's ear. `nodePort` is the new one, the number carved open on the nodes themselves, and it is not yours to pick freely: it must sit between 30000 and 32767. The API server refuses anything outside that range outright, with a message about the valid range, and the schema cannot save you because the range is a rule the live API enforces, so this task enforces it the same way.

Leaving `nodePort` out is also legal, and in production that is what you do: the API grabs a free one and you read it back after. Naming it is for when something outside is configured to aim at a specific port and must keep aiming there. This task names it, because a number you are graded on should be a number you wrote.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Service of type NodePort: named `{name}`, selecting `app: {name}`, with one port entry carrying `port: {port}`, `targetPort: {targetPort}`, and a `nodePort` you choose from the legal range.

## Rules
- one YAML document, one Service, nothing else in the file
- `apiVersion` is `v1`, and `spec.type` is `NodePort`
- one entry under `spec.ports`, carrying all three: `port: {port}`, `targetPort: {targetPort}`, and a `nodePort` of your own choosing
- the `nodePort` is an unquoted number between 30000 and 32767 inclusive. Anything outside is refused, the same way the API server refuses it
- the selector labels the pods it forwards to, as in the last task: `app: {name}`

## Hints
### Hint 1
Last task's ClusterIP, with one line added:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ...
spec:
  type: NodePort
  selector: ...
  ports: ...
```

`type` is the only new field at the top. The hole is carved in the ports entry.

### Hint 2
All three numbers in one entry:

```yaml
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

Read it out loud: "the cluster calls 80, the container listens on 8080, and the outside world hits any node on 30080". Pick your own nodePort, any number in the legal range.

### Hint 3
The range and why it looks like that: 30000 to 32767 sits high above the well-known ports, so a NodePort can never collide with something a node already runs, like ssh on 22. It is also small enough to be memorable. Two facts worth carrying around: a cluster client can still use the plain `port`, and if you ever see `nodePort: 8080` in the wild, it never made it to a cluster.
