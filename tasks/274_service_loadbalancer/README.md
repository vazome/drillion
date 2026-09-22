---
title: "LoadBalancer: the cloud's IP in front of the same three ports"
difficulty: medium
minutes: 15
prereqs: [273]
track: kubernetes
tags: [service, networking]
kind: manifest
---
# LoadBalancer: the cloud's IP in front of the same three ports

*Everything a NodePort is, a LoadBalancer is too, plus one thing only the cloud can give: an address the internet can find.*

## Read first
- [Service](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer): the LoadBalancer type on top of a NodePort

## Why
A NodePort makes the Service reachable on any node's IP, on a port in the legal range. That still leaves the client holding a node's address, and holding every node's address if one may be down. `type: LoadBalancer` hands the problem to whoever runs the cluster: the cloud provisions a load balancer with its own public IP and aims it at your nodes' NodePorts. From the manifest side, that whole sentence is one word of difference.

Which is the lesson: a LoadBalancer is not a third shape to learn. It is the same Service, the same selector, the same three port fields, `type` spelled differently. The changes are all outside the file, in the cloud's bill and the IP that appears in the Service's status after the balancer exists, which no schema will show you and this task cannot grade.

What the file must still get right is the part underneath. The selector still labels the pods. The three ports still agree with each other, and the nodePort still sits in its legal range, because the balancer's back end is the nodes' NodePorts. A LoadBalancer written without its NodePort foundations is a word typed over a shape that was never there.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Service of type LoadBalancer: named `{name}`, selecting `app: {name}`, with one port entry carrying `port: {port}`, `targetPort: {targetPort}`, and a `nodePort` in the legal range.

## Rules
- one YAML document, one Service, nothing else in the file
- `apiVersion` is `v1`, and `spec.type` is `LoadBalancer`
- one entry under `spec.ports`, carrying all three: `port: {port}`, `targetPort: {targetPort}`, and a `nodePort` of your own choosing between 30000 and 32767
- the selector labels the pods it forwards to: `app: {name}`
- nothing else new. If you catch yourself adding fields the last two tasks never had, the type change is the whole change

## Hints
### Hint 1
The NodePort you wrote, with one word changed:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ...
spec:
  type: LoadBalancer
  selector: ...
  ports: ...
```

That is the entire difference in the file. Everything else is the cloud's business.

### Hint 2
The ports entry, unchanged from last task:

```yaml
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

The balancer forwards to the nodes on `nodePort`, the nodes forward into the Service on `port`, and the container listens on `targetPort`. Pick your own nodePort in the legal range.

### Hint 3
How the three kinds stack, because they do not replace each other. A ClusterIP has an inside address. A NodePort is a ClusterIP that also opened a node port. A LoadBalancer is a NodePort that also bought a cloud IP. Each kind contains the previous one, which is why the file only ever grows by one line and why you can trace any Service back to the ClusterIP inside it.
