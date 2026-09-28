# Environments

What Settings, Environments shows for this repository. These rules live in the repository's
settings, not in any workflow file: a workflow only names the environment a job deploys to.

| Environment | Deployment branches | Protection rules |
|---|---|---|
| `dev` | any | none |
| `staging` | `main` only | none |
| `production` | `main` only | required reviewers: the `platform-leads` team; prevent self-review |

A job that names `production` waits, before its first step, until someone in
`platform-leads` approves that run. A job that names an environment not listed here creates
it, with no protection rules at all.
