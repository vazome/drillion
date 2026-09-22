---
title: "an Ingress: one address outside, a Service inside"
difficulty: medium
minutes: 15
prereqs: [272]
track: kubernetes
tags: [ingress, service, networking]
kind: manifest
---
# an Ingress: one address outside, a Service inside

*A LoadBalancer Service per app costs one cloud load balancer per app. An Ingress puts many apps behind one, and picks the Service by the host name and the path of each request.*

## Read first
- [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/): rules, paths, and the controller that makes them real

## Why
In 274 a LoadBalancer Service got its own address from the cloud. Do that for twenty services and you pay for twenty load balancers and hand out twenty addresses. Most companies instead run one HTTP proxy at the edge, and route by what is in the request: `shop.example.com` goes to one Service, `api.example.com/v2` to another.

An Ingress is that routing table, written as an object. On its own it does nothing: an Ingress controller, such as ingress-nginx or Traefik, watches Ingress objects and configures its proxy to match. A cluster can run more than one controller, and `ingressClassName` says which one this Ingress is for. Leave it out and the object may be picked up by the cluster's default controller, or by none, and nothing tells you which.

Each rule is a host, and under it a list of paths. `pathType: Prefix` matches the path and everything under it, split on `/`, so `/shop` matches `/shop/cart` and not `/shopping`. Each path points at a Service by name and port. The Service does the rest: the Ingress never talks to pods directly.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Ingress named `{name}`, handled by the `{ingressClass}` controller, that sends every request for `{host}` under `{path}` to the Service `{service}` on port `{port}`.

## Rules
- one Ingress, `apiVersion: networking.k8s.io/v1`
- `spec.ingressClassName` is `{ingressClass}`
- exactly one rule, for the host `{host}`
- that rule has exactly one path: `{path}`, with `pathType: Prefix`
- its backend is `service.name: {service}` and `service.port.number: {port}`

## Hints
### Hint 1
An Ingress is not a core object: it lives in the `networking.k8s.io` group.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ...
spec:
  ingressClassName: ...
  rules:
    - ...
```

### Hint 2
A rule is a host with an `http` block, and the paths are a list under that:

```yaml
  rules:
    - host: shop.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              ...
```

### Hint 3
The backend names the Service and one of its ports. A port can be given by `number` or by the Service port's `name`; this task asks for the number:

```yaml
            backend:
              service:
                name: storefront
                port:
                  number: 80
```
