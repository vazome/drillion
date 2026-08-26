# The tasks in a container: the image carries them, and the first run copies them into
# /data — a volume — where they can be written to, because a task file is where the
# learner's own code is stored. Mount a checkout at /data instead and it is used as-is,
# tasks and progress.json alike, so your work survives the image either way.

FROM node:24-slim AS web
WORKDIR /build
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY web/ ./
RUN pnpm build

# The wheel is built here rather than installed from source, so the image ships exactly
# what PyPI does: the app, the 171 tasks and the built page, all inside the package.
FROM python:3.13-slim AS wheel
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tasks/ ./tasks/
COPY --from=web /build/dist ./web/dist
RUN uv build --wheel -o /wheel

FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# The dependencies come from the lock; the project itself comes from the wheel above, so
# no src/ reaches this stage and `--no-install-project` is what stops uv looking for it.
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
