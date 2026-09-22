---
title: a CronJob that never runs twice at once, in the time zone you mean
difficulty: medium
minutes: 15
prereqs: [309]
track: kubernetes
tags: [workloads, job]
kind: manifest
---
# a CronJob that never runs twice at once, in the time zone you mean

*A CronJob makes a Job on a schedule. The schedule is five fields most people look up every time, and the three settings after it decide what happens when a run is slow.*

## Read first
- [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/): schedule syntax, time zones, concurrency policy and history limits

## Why
Nightly backups, hourly reports, a cleanup every Sunday. A CronJob holds a Job template and a schedule, and at each tick it creates a Job from the template.

The schedule is cron's five fields: minute, hour, day of month, month, day of week. `30 2 * * *` is 02:30 every day. Those times are read in the controller's time zone, which is usually UTC and rarely what the person asking for "2:30 at night" meant. `spec.timeZone` takes a name from the tz database, like `Europe/Berlin`, and moves the schedule there, daylight saving included.

A backup that usually takes ten minutes will one day take two hours, and the next tick arrives while it is still going. `concurrencyPolicy` decides what happens then. `Allow`, the default, starts a second copy beside the first, and two backups writing the same file is how you lose both. `Forbid` skips the new run. `Replace` stops the old one and starts the new.

Every run leaves a Job behind. `successfulJobsHistoryLimit` and `failedJobsHistoryLimit` say how many of each to keep, so there is a failed run's logs to read and not a year of them.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One CronJob named `{name}`, running `{image}` every day at `{time}` in the `{timeZone}` time zone, that never starts a run while the last one is still going, and keeps the last `{keep}` successful and `{keepFailed}` failed Jobs.

## Rules
- one CronJob, `apiVersion: batch/v1`
- `spec.schedule` fires once a day at `{time}`: minute and hour set, the other three fields `*`
- `spec.timeZone: {timeZone}`
- `spec.concurrencyPolicy: Forbid`
- `spec.successfulJobsHistoryLimit: {keep}` and `spec.failedJobsHistoryLimit: {keepFailed}`
- the Job template's pod has exactly one container, running `{image}`, and a `restartPolicy` of `Never` or `OnFailure`

## Hints
### Hint 1
A CronJob wraps a Job template, which wraps a pod template, so the container is three `spec`s deep:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ...
spec:
  schedule: "..."
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - ...
```

### Hint 2
Minute first, then hour. 06:05 every day is `5 6 * * *`, and 23:40 is `40 23 * * *`. Quote the whole schedule: an unquoted `*` at the start of a YAML value means something else entirely.

### Hint 3
The time zone and the three policy fields sit on the CronJob's own `spec`, beside `schedule`:

```yaml
  timeZone: Europe/Berlin
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
```
