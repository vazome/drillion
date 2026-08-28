# syntax=docker/dockerfile:1
FROM node:24-slim@sha256:ba849c60be29959425b8734d57b8b4b7d56f98edd9504c9af091d5281095a71e AS web
WORKDIR /build
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
RUN corepack enable
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --store-dir /pnpm/store
COPY web/ ./
RUN pnpm build

FROM python:3.13-slim@sha256:7ce4b6dfe35e55397b7cda544f8a13f191b7ae28dc5aad71fe664dbc9bc2623f AS wheel
# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /usr/local/bin/
ENV UV_LINK_MODE=copy
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tasks/ ./tasks/
COPY --from=web /build/dist ./web/dist
RUN --mount=type=cache,target=/root/.cache/uv uv build --wheel -o /wheel

FROM python:3.13-slim@sha256:7ce4b6dfe35e55397b7cda544f8a13f191b7ae28dc5aad71fe664dbc9bc2623f

# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /uvx /usr/local/bin/

# a base tag is a snapshot of Debian, and the digest pins above freeze that snapshot on
# purpose. This upgrade is what keeps the OS packages current regardless, so a pin can never
# mean a stale openssl.
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# no uv cache reaches the image: it lives only in the build cache mounts below, and a cache
# mount is never part of a layer. UV_LINK_MODE=copy is what lets a venv be filled from one.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# no src/ reaches this stage: the project comes from the wheel above, not the lock
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project
COPY --from=wheel /wheel/*.whl /tmp/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /app/.venv/bin/python --no-deps /tmp/*.whl && rm /tmp/*.whl

# basedpyright runs its language server with `node`; the npm bundled beside that node is
# never invoked, and its own dependencies are most of the image's CVE count. The `test`
# fails the build if the layout moves, so this can never quietly delete nothing.
RUN set -eu; \
    node_dir="$(echo /app/.venv/lib/python3.*/site-packages/nodejs_wheel)"; \
    test -x "$node_dir/bin/node"; \
    rm -rf "$node_dir/lib/node_modules/npm" "$node_dir/bin/npm" "$node_dir/bin/npx"

# the app runs out of /app/.venv, which uv fills without ever calling the interpreter's own
# pip. That pip is never invoked, and the versions its vendor.txt pins are the rest of the
# image's CVE count.
RUN set -eu; \
    sp="$(echo /usr/local/lib/python3.*/site-packages)"; \
    test -f "$sp/pip/_vendor/vendor.txt"; \
    rm -rf "$sp"/pip "$sp"/pip-*.dist-info /usr/local/bin/pip*

ENV PATH="/app/.venv/bin:$PATH" \
    DRILLION_ROOT=/data \
    DRILLION_HOST=0.0.0.0 \
    DRILLION_OPEN_BROWSER=0

RUN useradd --create-home --uid 1000 drillion && mkdir -p /data && chown drillion /data
USER drillion

EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/health')"
CMD ["drillion"]
