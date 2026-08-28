# syntax=docker/dockerfile:1
FROM node:25-slim AS web
WORKDIR /build
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
RUN corepack enable
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --store-dir /pnpm/store
COPY web/ ./
RUN pnpm build

FROM python:3.13-slim AS wheel
# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /usr/local/bin/
ENV UV_LINK_MODE=copy
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tasks/ ./tasks/
COPY --from=web /build/dist ./web/dist
RUN --mount=type=cache,target=/root/.cache/uv uv build --wheel -o /wheel

FROM python:3.13-slim

# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /uvx /usr/local/bin/

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
