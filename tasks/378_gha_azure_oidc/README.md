---
title: "OIDC to Azure: deploy to AKS without a stored secret"
difficulty: hard
minutes: 20
prereqs: [377]
track: github-actions
tags: [permissions, azure, environments]
kind: workflow
edits: .github/workflows/deploy.yml
---
# OIDC to Azure: deploy to AKS without a stored secret

*A client secret in the repository's settings is a password that never expires and anyone with the workflow can use. With OIDC, GitHub hands the job a short-lived token that Azure trusts, and there is no secret to leak.*

## Read first
- [OpenID Connect in Azure](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure): the federated credential and the workflow side
- [azure/login](https://github.com/Azure/login#login-with-openid-connect-oidc-recommended): the inputs for OIDC

## Why
The old way to let a workflow into Azure was a service principal's client secret, stored as a repository secret. It works until it leaks, expires on a Friday, or is copied into a second repository nobody remembers.

**OIDC** replaces it. Azure is told once, in a *federated credential* on an app registration, to trust tokens from GitHub for one repository and one environment. At run time the job asks GitHub for a token saying exactly that, and `azure/login` trades it for an Azure session. Nothing long-lived is stored anywhere.

Three things make it work. The job needs `permissions: id-token: write`, or GitHub will not issue the token; since a job-level block replaces the workflow's, it also needs `contents: read` to check out. The job names its `environment`, because that is what the federated credential's subject matches: a token from any other environment is refused. And `azure/login` gets the app's client ID, the tenant ID and the subscription ID, which are identifiers, not secrets, so they live in repository **variables**, read through the `vars` context, and there is no `creds` input at all.

## You get
An empty `.github/workflows/deploy.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run and nothing signs in.

## You return
A workflow named `deploy`, run on pushes to `main`, whose one job `deploy` runs in the `production` environment, signs in to Azure with OIDC using the IDs in repository variables, fetches credentials for the AKS cluster `{cluster}` in the resource group `{group}`, and applies the production overlay.

## Rules
- `name: deploy`, and `on` is exactly `push` with `branches: [main]`
- exactly one job, `deploy`, on `ubuntu-latest`, with `environment: production` and `permissions` exactly `id-token: write` and `contents: read`
- its steps, in order: `actions/checkout` at any version; `azure/login` at any version with exactly `client-id: ${{{{ vars.AZURE_CLIENT_ID }}}}`, `tenant-id: ${{{{ vars.AZURE_TENANT_ID }}}}` and `subscription-id: ${{{{ vars.AZURE_SUBSCRIPTION_ID }}}}`; `run: az aks get-credentials --resource-group {group} --name {cluster}`; `run: kubectl apply -k k8s/overlays/production`
- no secret anywhere in the workflow: no `secrets.` expression and no `creds` input

## Hints
### Hint 1
The token is a permission like any other, and the environment is one line on the job:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions:
      id-token: write
      contents: read
```

### Hint 2
Repository variables are read like secrets, through their own context:

```yaml
      - uses: azure/login@v3
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
```

### Hint 3
Once signed in, the Azure CLI writes a kubeconfig for the cluster, and kubectl uses it:

```yaml
      - run: az aks get-credentials --resource-group rg-shop-prod --name aks-shop-prod
      - run: kubectl apply -k k8s/overlays/production
```
