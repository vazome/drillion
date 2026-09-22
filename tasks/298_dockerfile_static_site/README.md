---
title: "a static site: build with Node, serve with nginx"
difficulty: hard
minutes: 20
prereqs: [291, 296]
track: docker
tags: [multi-stage]
kind: docker
edits: Dockerfile
---
# a static site: build with Node, serve with nginx

*Node is needed for one minute, to build. For the next six months, the site is files, and nginx serves files.*

## Read first
- [npm ci](https://docs.npmjs.com/cli/commands/npm-ci): installing exactly what the lockfile says
- [nginx-unprivileged](https://hub.docker.com/r/nginxinc/nginx-unprivileged): nginx built to run as a non-root user

## Why
A frontend is built with Node and runs in a browser. The container never needs Node after the build: what it serves is the `dist/` folder the build writes, HTML, JavaScript and CSS. So the build stage is a Node image and the final stage is a web server, and the one thing that crosses between them is `dist/`.

The build stage uses the layer cache the same way a Python one does. `package.json` and `package-lock.json` go in first, alone, and `npm ci` installs from them; the source follows, and only then the build. `npm ci` and not `npm install`: `install` resolves versions again and may rewrite the lockfile, `ci` installs exactly what the lockfile pins, or stops with an error.

The official `nginx` image starts as root to listen on port 80. `nginxinc/nginx-unprivileged` is the same nginx built to run as a normal user on 8080, which is what a cluster that refuses root containers will accept. Its web root is `/usr/share/nginx/html`, and its `CMD` already starts nginx, so the final stage needs no `CMD` of its own.

## You get
A build context with a small status page: `package.json`, its lockfile, `build.mjs`, `index.html` and `src/main.js`. `npm run build` writes the finished site into `dist/`.

## You return
A two-stage Dockerfile that builds the site with Node `{node}` and serves `dist/` with `nginxinc/nginx-unprivileged:{nginx}`.

## Rules
- the first stage is `FROM node:{node}-slim`, named, with a `WORKDIR`
- `package.json` and `package-lock.json` are copied on their own, then `RUN npm ci`, then the rest of the source, then `RUN npm run build`
- the second stage is `FROM nginxinc/nginx-unprivileged:{nginx}`, copies only `dist` from the first stage into `/usr/share/nginx/html`, and runs nothing
- `EXPOSE 8080`

## Hints
### Hint 1
The first stage is the layer cache task again, with npm in place of pip. The second stage is two lines and an `EXPOSE`.

### Hint 2
Copying two files into a directory needs the destination to end in a slash: `COPY package.json package-lock.json ./`. With `WORKDIR /app`, the build writes `/app/dist`, and that is the path the second stage copies from.

### Hint 3
The same split for a site built with a different tool:

```dockerfile
FROM node:22-slim AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /web/build /usr/share/nginx/html
EXPOSE 8080
```

Where the build writes depends on the tool: `dist`, `build` or `out`. This task's `build.mjs` writes `dist`.
