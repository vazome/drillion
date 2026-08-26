# The drills in a container: same app, exercises/ and progress.json mounted from
# the host so your work survives the image.

FROM node:24-slim AS web
WORKDIR /build
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY web/ ./
RUN pnpm build

FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# Only web/dist is ever served, and the API runs without it. No package.json reaches
# this stage, so `build_web()` finds nothing to build and leaves the baked dist alone.
COPY --from=web /build/dist ./web/dist

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
