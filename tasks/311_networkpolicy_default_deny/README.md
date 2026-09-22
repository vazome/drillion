---
title: "NetworkPolicy: deny everything, then let one app in"
difficulty: hard
minutes: 20
prereqs: [272]
track: kubernetes
tags: [kubernetes, networkpolicy, networking, labels, multi-document]
kind: manifest
---
# NetworkPolicy: deny everything, then let one app in

*Out of the box, every pod in a cluster can reach every other pod. A NetworkPolicy turns that into a list of who may talk to whom, and the list starts with nobody.*

## Read first
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/): how policies select pods, and how they add up
- [Default policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/#default-policies): the empty selector that means "every pod"

## Why
If an attacker gets into one pod, the flat network lets them reach the database, the payments service and anything else with an open port. Network policies are how a cluster says which pods may connect to which, the way a firewall does, but by label instead of by IP address.

The rules are additive, and that shapes how they are written. A pod no policy selects accepts everything. Once any policy selects a pod for `Ingress`, it accepts only what some policy allows. So the usual pattern is two policies. The first selects every pod in the namespace, with an empty `podSelector`, lists `Ingress` in `policyTypes`, and allows nothing: that is "default deny". Every later policy opens one door, such as "pods labelled `app: api` accept connections from pods labelled `app: web`, on port 8080".

The policies only work if the cluster's network plugin enforces them. Calico and Cilium do; some simpler plugins accept the objects and ignore them, which is worth checking before you rely on it.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two NetworkPolicies in one file. The first, `default-deny`, blocks all incoming traffic to every pod in the namespace. The second, `{name}`, lets pods labelled `app: {client}` reach pods labelled `app: {target}` on TCP port `{port}`, and nothing else.

## Rules
- two YAML documents, separated by `---`, both `apiVersion: networking.k8s.io/v1`, `kind: NetworkPolicy`
- the first is named `default-deny`, has an empty `podSelector`, lists only `Ingress` in `policyTypes`, and has no `ingress` rules
- the second is named `{name}`, selects the pods with `matchLabels` `app: {target}`, and lists only `Ingress` in `policyTypes`
- it has exactly one `ingress` rule, whose `from` has exactly one entry: a `podSelector` matching `app: {client}`
- that rule's `ports` has exactly one entry: TCP, port `{port}`

## Hints
### Hint 1
Default deny is the smallest policy there is. The empty selector selects every pod, and naming `Ingress` without any rules allows none of it:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {{}}
  policyTypes:
    - Ingress
```

### Hint 2
In the second policy, `podSelector` at the top of the spec picks the pods being protected, and the one inside `from` picks who may connect to them:

```yaml
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: web
```

### Hint 3
`ports` sits beside `from`, in the same rule, and the protocol defaults to TCP if you leave it out:

```yaml
      ports:
        - protocol: TCP
          port: 8080
```
