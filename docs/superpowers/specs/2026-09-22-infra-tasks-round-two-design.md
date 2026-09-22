# Infra tasks, round two

Twenty-five tasks, 299 to 323, over the Kubernetes, Helm and Docker tracks. The first round
taught the shape of each object; this one teaches what makes it fit for production.

## Delivery

Four PRs, in this order, each on its own branch off `main`:

1. **Production-ready Kubernetes, 299 to 305.** Existing schemas, no grader change.
2. **New Kubernetes objects, 306 to 313.** Nine schemas added at the pinned 1.34.11.
3. **Helm like real charts, 314 to 318.** `EDITS` widens to allow `_helpers.tpl`.
4. **Docker hardening, 319 to 323.** No grader change; hadolint enforces DL4006 already.

## 1. Production-ready Kubernetes

| # | Task | Level |
|---|---|---|
| 299 | readiness and liveness probes | medium |
| 300 | a startup probe for a slow boot | medium |
| 301 | requests and limits, Guaranteed QoS | medium |
| 302 | a hardened pod, the restricted standard | hard |
| 303 | rollout strategy: maxSurge, maxUnavailable, minReadySeconds | medium |
| 304 | an init container preparing a shared emptyDir | hard |
| 305 | a ConfigMap mounted as files | medium |

## 2. New Kubernetes objects

Schemas added from `yannh/kubernetes-json-schema` at 1.34.11 standalone-strict: Ingress,
HorizontalPodAutoscaler (autoscaling/v2), Job, CronJob, NetworkPolicy, ServiceAccount, Role,
RoleBinding, PodDisruptionBudget. `manifest.json` records the new digest.

The digest feeds every `m1:` and `h1:` fingerprint, so verdicts graded after the change carry
a new one. A fingerprint is provenance on an archived verdict and nothing regrades against
it, so old archives keep theirs and nothing else moves.

| # | Task | Level |
|---|---|---|
| 306 | Ingress: host and path to a Service | medium |
| 307 | Ingress with TLS from a Secret | medium |
| 308 | HPA on CPU, beside the Deployment it scales | hard |
| 309 | a Job: completions, backoffLimit, ttl cleanup | easy |
| 310 | a CronJob: schedule, concurrencyPolicy, history limits | medium |
| 311 | NetworkPolicy: default deny, then allow one app in | hard |
| 312 | least privilege: ServiceAccount, Role, RoleBinding | hard |
| 313 | a PodDisruptionBudget | easy |

## 3. Helm like real charts

`values.schema.json` is shipped by the chart and read-only; the learner writes `values.yaml`
against it, so no new editable file type is needed.

| # | Task | Level |
|---|---|---|
| 314 | `_helpers.tpl`: define a fullname and labels | medium |
| 315 | include the helpers with `nindent` in a Deployment | medium |
| 316 | `required` and `fail` | medium |
| 317 | `values.yaml` against a chart's `values.schema.json` | easy |
| 318 | `range` over a list making several resources | hard |

## 4. Docker hardening

| # | Task | Level |
|---|---|---|
| 319 | HEALTHCHECK without curl | easy |
| 320 | `SHELL` with pipefail before a piped download | medium |
| 321 | a BuildKit cache mount for pip | medium |
| 322 | a secret mount for a private index token | hard |
| 323 | JVM multi-stage: Maven build, JRE runtime | hard |

## Every task

- README frontmatter and sections in the house shape; the Why in plain business words.
- The answer key passes for every seed, and a `BREAKS` row per displayed rule fails.
- selfcheck, doctor, pytest and ruff pass; verified in the image.
- Facts checked against the Kubernetes, Helm and Docker docs through Context7.
- Task counts updated wherever the docs state them.
