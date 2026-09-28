---
title: "canary analysis: let Prometheus decide whether the release goes on"
difficulty: hard
minutes: 25
prereqs: [367]
track: argocd
tags: [canary, multi-document]
kind: manifest
---
# canary analysis: let Prometheus decide whether the release goes on

*A pause waits; an analysis step measures. An AnalysisTemplate asks Prometheus how the canary is doing, and a failed answer rolls the release back before anyone is paged.*

## Read first
- [Analysis & Progressive Delivery: Inline Analysis](https://argoproj.github.io/argo-rollouts/features/analysis/#inline-analysis): an analysis as a step, and `count` with `interval`
- [Prometheus](https://argoproj.github.io/argo-rollouts/analysis/prometheus/): the provider, and why `result[0]`

## Why
A timed pause only gives a human the chance to look, and at 3am nobody looks. An **analysis step** makes the rollout look for itself: it starts an AnalysisRun from an **AnalysisTemplate**, blocks the rollout until the run finishes, and goes on only if the run succeeds. If it fails, Argo Rollouts aborts: traffic goes back to the old version and the Rollout is marked Degraded.

The template holds the measurement. A `metric` has a `provider`, here Prometheus with its `address` and a PromQL `query`, and a `successCondition` over the result. Prometheus answers a query with a vector, so the condition reads `result[0]`. The template takes `args`, so one template serves every service: the query reads the argument as `args.service-name` in double curly braces, and the Rollout's step passes the value.

How long it measures is `interval` and `count`: every `interval`, `count` times. Leave `count` out and a metric with an interval measures until something stops it, and inside a step nothing does, so the rollout waits forever. `failureLimit` says how many failed measurements to tolerate before the whole analysis fails: one bad minute should not roll back a release, three should.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the Argo Rollouts schema when you run it, offline. Nothing is measured: the template and the steps are read, not run.

## You return
Two documents: an AnalysisTemplate `{template}` that asks Prometheus for a service's success rate every minute, five times, and fails after {limit} measurements below {threshold}; and the Rollout `{name}` that sends 20% of traffic to a new version, runs that analysis on `{service}`, then goes to 50% and waits ten minutes.

## Rules
- two documents: the AnalysisTemplate, then the Rollout, both `apiVersion: argoproj.io/v1alpha1`
- the AnalysisTemplate is named `{template}`, and its `spec.args` is exactly one argument, `name: service-name`, with no value
- it has exactly one metric, `name: success-rate`, with `interval: 1m`, `count: 5`, `failureLimit: {limit}` and `successCondition: result[0] >= {threshold}`
- the metric's provider is `prometheus`, with `address: {address}` and exactly this `query`: `{query}`
- the Rollout is named `{name}`, with `replicas: 10`, a selector of `app: {name}` that matches its pod template's labels, and one container, `{name}`, running `{image}`
- its `spec.strategy.canary.steps` is exactly four steps, in this order: `setWeight: 20`; an analysis whose `templates` is exactly `[{{templateName: {template}}}]` and whose `args` is exactly `[{{name: service-name, value: {service}}}]`; `setWeight: 50`; and a pause of `duration: 10m`

## Hints
### Hint 1
The template's argument is declared with a name only; the step supplies its value. The query reads it in double braces:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: checkout-success-rate
spec:
  args:
    - name: service-name
```

### Hint 2
One metric, measured on a schedule, judged by a condition over Prometheus's vector:

```yaml
  metrics:
    - name: success-rate
      interval: 1m
      count: 5
      failureLimit: 3
      successCondition: result[0] >= 0.99
      provider:
        prometheus:
          address: http://prometheus.monitoring.svc:9090
          query: sum(rate(...))
```

### Hint 3
The analysis step names the template and passes the argument:

```yaml
        - setWeight: 20
        - analysis:
            templates:
              - templateName: checkout-success-rate
            args:
              - name: service-name
                value: checkout
```
