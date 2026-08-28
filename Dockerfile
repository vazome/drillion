FROM node:24-slim AS web
WORKDIR /build
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY web/ ./
RUN pnpm build

FROM python:3.13-slim AS wheel
# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /usr/local/bin/
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tasks/ ./tasks/
COPY --from=web /build/dist ./web/dist
RUN uv build --wheel -o /wheel

FROM python:3.13-slim

# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /uvx /usr/local/bin/

WORKDIR /app
# UV_NO_CACHE: the image runs as drillion, so a wheel cache under /root only adds weight
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_CACHE=1

# no src/ reaches this stage: the project comes from the wheel above, not the lock
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY --from=wheel /wheel/*.whl /tmp/
RUN uv pip install --python /app/.venv/bin/python --no-deps /tmp/*.whl && rm /tmp/*.whl

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
