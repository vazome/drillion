# The drills in a container: same app, exercises/ and progress.json mounted from
# the host so your work survives the image.
#
# The frontend build stage lands here in Task 6, and `COPY --from=web` below:
# FROM node:24-slim AS web
# WORKDIR /build
# COPY web/package.json web/pnpm-lock.yaml ./
# RUN corepack enable && pnpm install --frozen-lockfile
# COPY web/ ./
# RUN pnpm build

FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# Whatever has been built for the browser: only web/dist is ever served, and the
# API runs without it. Task 6 replaces this with `COPY --from=web /build/dist`.
COPY web/ ./web/

ENV PATH="/app/.venv/bin:$PATH" \
    STUDY_ROOT=/data \
    STUDY_HOST=0.0.0.0 \
    STUDY_OPEN_BROWSER=0

RUN useradd --create-home --uid 1000 study && mkdir -p /data && chown study /data
USER study

EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/health')"
CMD ["study"]
