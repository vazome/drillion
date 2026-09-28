---
title: "build and push to ACR: signed in with OIDC, layers cached"
difficulty: hard
minutes: 20
prereqs: [378]
track: github-actions
tags: [azure, caching, releases]
kind: workflow
edits: .github/workflows/image.yml
---
# build and push to ACR: signed in with OIDC, layers cached

*A tag is a release, and a release is an image in the registry. This workflow signs in to Azure with no stored password, builds with Buildx, and reuses the layers the last build made.*

## Read first
- [Authenticate with an Azure container registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication): `az acr login` on top of an Azure session
- [Cache management with GitHub Actions](https://docs.docker.com/build/ci/github-actions/cache/#github-cache): the `gha` cache backend

## Why
Pushing to Azure Container Registry needs a registry login. Once `azure/login` has signed the job in with OIDC, `az acr login --name <registry>` turns that Azure session into a Docker credential for the registry, so no registry password or admin user is ever stored anywhere.

`docker/build-push-action` builds and pushes in one step. Tagging the image with `github.ref_name`, the short name of the tag that started the run, makes the registry's tags match the repository's releases one for one.

A Docker build on a fresh runner starts with no layers at all, so every build reinstalls every dependency. The build action can store its layer cache in the GitHub Actions cache with `cache-from: type=gha` and `cache-to: type=gha,mode=max`, where `mode=max` keeps the layers of every stage, not just the final one. The default Docker driver cannot export a cache, so `docker/setup-buildx-action` comes first and creates a builder that can.

## You get
An empty `.github/workflows/image.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run and nothing signs in.

## You return
A workflow named `image`, run when a tag starting with `v` is pushed, whose one job `image` signs in to Azure with OIDC, logs Docker in to the registry `{acr}`, sets up Buildx, and builds and pushes `{acr}.azurecr.io/{repository}` tagged with the release, reusing and saving its layer cache in GitHub Actions.

## Rules
- `name: image`, and `on` is exactly `push` with `tags: ["v*"]`
- exactly one job, `image`, on `ubuntu-latest`, with `permissions` exactly `id-token: write` and `contents: read`
- its steps, in order: `actions/checkout` at any version; `azure/login` at any version with exactly `client-id`, `tenant-id` and `subscription-id` from `vars.AZURE_CLIENT_ID`, `vars.AZURE_TENANT_ID` and `vars.AZURE_SUBSCRIPTION_ID`; `run: az acr login --name {acr}`; `docker/setup-buildx-action` at any version, with no inputs; `docker/build-push-action` at any version
- the build's inputs are exactly `context: .`, `push: true`, `tags: {tags}`, `cache-from: type=gha` and `cache-to: type=gha,mode=max`
- no secret anywhere in the workflow

## Hints
### Hint 1
The Azure session from `azure/login` is what `az acr login` trades for a registry login:

```yaml
      - run: az acr login --name acmeshop
```

### Hint 2
Buildx is one step with nothing to configure:

```yaml
      - uses: docker/setup-buildx-action@v4
```

### Hint 3
The cache is two inputs on the build step, one to read and one to write:

```yaml
      - uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          tags: acmeshop.azurecr.io/shop/web:${{ github.ref_name }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```
