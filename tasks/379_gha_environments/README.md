---
title: "environments: promote one build from dev to staging to production"
difficulty: hard
minutes: 20
prereqs: [373]
track: github-actions
tags: [environments, needs, concurrency]
kind: workflow
edits: .github/workflows/release.yml
---
# environments: promote one build from dev to staging to production

*An environment is where a job deploys to, and the gate in front of it. The workflow names the environments in order; the repository's settings decide who has to approve.*

## Read first
- [Managing environments for deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments): protection rules, reviewers and branches
- [Workflow syntax: jobs.job_id.environment](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idenvironment): `name` and `url`
- [Workflow syntax: jobs.job_id.concurrency](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idconcurrency): one deploy at a time

## Why
A release goes to dev, then staging, then production, and each step should only happen once the one before it worked. Three jobs chained with `needs` give the order. The `environment` on each job gives the gate: a job that names an environment waits until that environment's protection rules are satisfied, and its secrets and variables are only handed to jobs that name it.

The rules themselves are not in the workflow. Required reviewers, wait timers and which branches may deploy are set in the repository's settings, and `ENVIRONMENTS.md` beside your file shows what this repository has: production needs an approval from `platform-leads`. So the workflow's job is to name the right environment on the right job, spelt exactly, since a job naming an environment that does not exist creates a new one with no protection at all.

`environment` can carry a `url`, and GitHub shows it on the run and in the repository's list of deployments, which is where people look for what is live.

Two runs deploying to the same place at once is its own outage. `concurrency` on a job puts it in a named group, and a second job in the same group waits for the first. `cancel-in-progress: false` keeps a deploy that has started from being killed halfway.

## You get
An empty `.github/workflows/release.yml`, and beside it `ENVIRONMENTS.md`, read-only: the environments this repository has and their rules. Whatever you type is linted by actionlint when you run it, offline. Nothing is run, and whether a reviewer is really required is a setting no file can prove: the grader checks that your workflow names the environments and orders the jobs as they are meant to be.

## You return
A workflow named `release`, run on pushes to `main`, with three jobs that deploy `{app}` in order: to `dev`, then `staging` once dev succeeded, then `production` once staging succeeded, each showing its URL, and each never running twice at once.

## Rules
- `name: release`, and `on` is exactly `push` with `branches: [main]`
- three jobs, `deploy-dev`, `deploy-staging` and `deploy-production`, each on `ubuntu-latest`
- `deploy-dev` needs nothing; `deploy-staging` has `needs: deploy-dev`; `deploy-production` has `needs: deploy-staging`
- each job's `environment` has exactly a `name` and a `url`: `dev` at `{dev_url}`, `staging` at `{staging_url}`, `production` at `{production_url}`
- each job's `concurrency` is exactly `group: deploy-<environment>`, as in `deploy-dev`, with `cancel-in-progress: false`
- each job's steps, in order: `actions/checkout` at any version; `run: ./deploy.sh <environment>`, as in `./deploy.sh dev`

## Hints
### Hint 1
An environment with a URL is a small map:

```yaml
    environment:
      name: staging
      url: https://staging.cart.acme.io
```

### Hint 2
A job-level concurrency group, never cancelled once it starts:

```yaml
    concurrency:
      group: deploy-staging
      cancel-in-progress: false
```

### Hint 3
The chain is one `needs` per job, each on the one before:

```yaml
  deploy-production:
    needs: deploy-staging
```
