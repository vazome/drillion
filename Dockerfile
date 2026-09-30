# syntax=docker/dockerfile:1
FROM node:26-slim@sha256:ec7758ee051e457b468b32bde57b0879010b325bb9862718e9615225ce4aaae1 AS web
WORKDIR /build
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
# node images no longer bundle corepack. It stays the mechanism because it reads the pnpm version
# out of package.json's packageManager, which keeps that pin the only place the version is
# written. Unpacked from its checksummed release tarball rather than `npm install -g`, which
# cannot pin by hash; the package has no dependencies, so unpacking it is the whole install.
ADD --checksum=sha256:f62535fc7be1f77e4b12cd1e420b8542b8e895cbb14178926963a41a9232a4fe \
    https://registry.npmjs.org/corepack/-/corepack-0.35.0.tgz /tmp/corepack.tgz
RUN mkdir /opt/corepack && tar -xzf /tmp/corepack.tgz -C /opt/corepack --strip-components=1 \
    && node /opt/corepack/dist/corepack.js enable --install-directory /usr/local/bin pnpm
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --store-dir /pnpm/store
COPY web/ ./
# the install above already ran the lockfile; pnpm 11's pre-run check would re-run it without
# --store-dir, see a different storeDir in .modules.yaml, and abort trying to purge node_modules
ENV PNPM_CONFIG_VERIFY_DEPS_BEFORE_RUN=false
RUN pnpm build

FROM python:3.14-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS wheel
# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /usr/local/bin/
ENV UV_LINK_MODE=copy
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tasks/ ./tasks/
COPY --from=web /build/dist ./web/dist
RUN --mount=type=cache,target=/root/.cache/uv uv build --wheel -o /wheel

FROM python:3.14-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS runtime

# v0.12.7
COPY --from=ghcr.io/astral-sh/uv@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 /uv /uvx /usr/local/bin/

# a base tag is a snapshot of Debian, and the digest pins above freeze that snapshot on
# purpose. This upgrade is what keeps the OS packages current regardless, so a pin can never
# mean a stale openssl. git, less, nano and vim-tiny are the git track's terminal (ADR 0013).
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git less nano vim-tiny \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# no uv cache reaches the image: it lives only in the build cache mounts below, and a cache
# mount is never part of a layer. UV_LINK_MODE=copy is what lets a venv be filled from one.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# no src/ reaches this stage: the project comes from the wheel above, not the lock
COPY pyproject.toml uv.lock README.md ./
# basedpyright runs its language server with `node`; the npm bundled beside that node is never
# invoked, and its own dependencies are most of the image's CVE count. Removing it in the same
# RUN that installs it keeps it out of the image rather than merely out of the final layer's
# view: a later RUN's rm only hides files an earlier layer already shipped, it does not shrink
# anything. The `test` fails the build if the layout moves, so this can never quietly delete
# nothing.
RUN --mount=type=cache,target=/root/.cache/uv \
    set -eu; \
    uv sync --locked --no-dev --no-install-project; \
    node_dir="$(echo /app/.venv/lib/python3.*/site-packages/nodejs_wheel)"; \
    test -x "$node_dir/bin/node"; \
    rm -rf "$node_dir/lib/node_modules/npm" "$node_dir/bin/npm" "$node_dir/bin/npx"
COPY --from=wheel /wheel/*.whl /tmp/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /app/.venv/bin/python --no-deps /tmp/*.whl && rm /tmp/*.whl

# the app runs out of /app/.venv, which uv fills without ever calling the interpreter's own
# pip. That pip is never invoked, and the versions its vendor.txt pins are the rest of the
# image's CVE count.
RUN set -eu; \
    sp="$(echo /usr/local/lib/python3.*/site-packages)"; \
    test -f "$sp/pip/_vendor/vendor.txt"; \
    rm -rf "$sp"/pip "$sp"/pip-*.dist-info /usr/local/bin/pip*

ENV PATH="/app/.venv/bin:$PATH" \
    DRILLION_ROOT=/data \
    DRILLION_TOOLS_DIR=/app/tools \
    DRILLION_HOST=0.0.0.0 \
    DRILLION_OPEN_BROWSER=0

RUN useradd --create-home --uid 1000 drillion && mkdir -p /data /app/tools && chown drillion /data /app/tools
USER drillion
# /data is normally a bind mount, so keep the pinned grader in the image rather than under the
# mount. `doctor --fetch` verifies the downloaded binary before this layer is accepted.
#
# `doctor` also walks the whole task catalogue, which only the installed package (this stage's
# wheel, tasks included) can do, so this RUN cannot move earlier or shrink to just tools.py: a
# src/ or tasks/ change reruns it every time regardless. What a cache mount avoids is the
# network part of that rerun -- `tools.installed` finds a pin's binary already sitting in the
# cache and verifies its checksum instead of downloading it again, so only an actual pin change
# in tools.py reaches the network.
RUN --mount=type=cache,id=drillion-tools,target=/home/drillion/.cache/drillion-tools,uid=1000 \
    DRILLION_TOOLS_DIR=/home/drillion/.cache/drillion-tools drillion doctor --fetch && \
    cp -a /home/drillion/.cache/drillion-tools/. /app/tools/

EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/health')"
CMD ["drillion"]
