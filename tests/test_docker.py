"""Every rule a Dockerfile task shows the learner is one its grader enforces, through the real
pipeline: hadolint, the build-context check and `check()`, in the sandbox, as a submission is.

Each row replaces one piece of the answer key and must fail. A rule with no row here is a
rule a wrong answer can pass."""

import asyncio
import shutil
import tempfile
import uuid
from pathlib import Path

import httpx
import pytest

from drillion import catalogue, grading, kinds, manifest, runner, state, tools
from drillion.api import app
from drillion.settings import settings

BS = "\\"
# (what in the answer key, what to put instead); `{uid}` and the like are the brief's
BREAKS = {
    "289_dockerfile_first_image": [
        ('CMD ["python", "app.py"]', "CMD python app.py"),
        ("COPY app.py .", "COPY main.py ."),
        ("COPY app.py .", "COPY . ."),
        ("-slim", ""),
        ("WORKDIR /app\n", ""),
        ("ENV PORT={port}", "ENV PORT=1"),
        ("EXPOSE {port}", "EXPOSE 80"),
    ],
    "290_dockerfile_layer_cache": [
        (
            (
                "COPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY app.py ."
            ),
            "COPY . .\nRUN pip install --no-cache-dir -r requirements.txt",
        ),
        ("--no-cache-dir ", ""),
        ('"0.0.0.0"', '"127.0.0.1"'),
        ('"--port", "{port}"', '"--port", "8001"'),
        ("COPY app.py .\n", ""),
        ("-r requirements.txt", "fastapi uvicorn"),
    ],
    "291_dockerfile_non_root": [
        (" -l app", " app"),
        ("USER {uid}", "USER app"),
        ("USER {uid}", "USER 0"),
        ("--chown={uid}:{uid} ", ""),
        ("CMD", "RUN chmod 755 app.py\nCMD"),
        ("--uid {uid}", "--uid 1234"),
    ],
    "292_dockerfile_arg_env": [
        ("ARG PYTHON_VERSION", "#ARG PYTHON_VERSION"),
        ("ENV APP_VERSION=${APP_VERSION}", "ENV APP_VERSION={version}"),
        ("    LOG_LEVEL={level}", "    LOG=x"),
        ("ARG APP_VERSION=", "ENV APP_VERSION="),
        ("FROM python:${PYTHON_VERSION}-slim", "FROM python:{python}-slim"),
    ],
    "293_dockerfile_apt": [
        ("--no-install-recommends ", ""),
        (f"update {BS}\n    && apt-get", "update\nRUN apt-get"),
        (f"{BS}\n    && rm -rf", "\nRUN rm -rf"),
        ("ca-certificates", "ca-certificates curl"),
        ("apt-get install", "apt install"),
        ("apt-get update", "apt-get update && apt-get upgrade -y"),
    ],
    "294_dockerfile_entrypoint_cmd": [
        ('ENTRYPOINT ["python", "worker.py"]\nCMD ["', 'CMD ["python", "worker.py", "'),
        ('ENTRYPOINT ["python", "worker.py"]', "ENTRYPOINT python worker.py"),
        (
            'ENTRYPOINT ["python", "worker.py"]',
            'ENTRYPOINT ["python", "worker.py", "--queue", "x"]',
        ),
        ('"--concurrency", "{concurrency}"', '"--concurrency={concurrency}"'),
    ],
    "295_dockerfile_pinned_base": [
        ("@sha256:{digest}", ""),
        ("@sha256:{digest}", "@sha256:" + "0" * 64),
        ("ARG REVISION\n", ""),
        ('"${REVISION}"', '"abc123"'),
        ("image.source", "image.url"),
    ],
    "296_dockerfile_multistage_go": [
        ("CGO_ENABLED=0 ", ""),
        (" AS build", ""),
        (":nonroot", ":latest"),
        ("EXPOSE", "RUN echo hi\nEXPOSE"),
        ("--from=build", "--from=builder"),
        ("static-debian12:nonroot", "static-debian12:nonroot\nCOPY main.go /main.go"),
        ("gcr.io/distroless/static-debian12:nonroot", "golang:{go}"),
        ('ENTRYPOINT ["/{name}"]', 'ENTRYPOINT ["/out/{name}"]'),
    ],
    "297_dockerfile_multistage_python": [
        ('ENV PATH="/opt/venv/bin:$PATH"\nWORKDIR /build', "WORKDIR /build"),
        ("/opt/venv /opt/venv", "/opt/venv /venv"),
        (
            "WORKDIR /app",
            "RUN pip install --no-cache-dir fastapi==0.141.1\nWORKDIR /app",
        ),
        (" AS build", " AS build\nFROM python:3.11-slim"),
        ('/opt/venv\nENV PATH="/opt/venv/bin:$PATH"', "/opt/venv"),
        ("FROM python:{python}-slim\n", "FROM python:3.11-slim\n"),
        ('"--host", "0.0.0.0"', '"--host", "127.0.0.1"'),
    ],
    "298_dockerfile_static_site": [
        ("npm ci", "npm install"),
        ("COPY package.json package-lock.json ./\n", ""),
        ("/app/dist", "/app"),
        ("EXPOSE 8080", "EXPOSE 80"),
        ("nginx-unprivileged", "nginx"),
        ("COPY . .\nRUN npm run build", "RUN npm run build\nCOPY . ."),
    ],
    "319_dockerfile_healthcheck": [
        ("--interval={interval}s", "--interval=99s"),
        ("--timeout=3s ", ""),
        ("--timeout=3s", "--timeout=60s"),
        (
            (
                '["python", "-c", "import urllib.request; '
                "urllib.request.urlopen('http://localhost:{port}/health', timeout=2)\"]"
            ),
            '["curl", "-f", "http://localhost:{port}/health"]',
        ),
        (
            (
                'CMD ["python", "-c", "import urllib.request; '
                "urllib.request.urlopen('http://localhost:{port}/health', timeout=2)\"]"
            ),
            "CMD python -c 'import urllib.request'",
        ),
        ("localhost:{port}/health", "localhost:{port}/orders"),
        ("localhost:{port}/health", "localhost:1/health"),
        ("HEALTHCHECK", "RUN apt-get update && apt-get install -y curl\nHEALTHCHECK"),
        ('"--port", "{port}"]', '"--port", "1"]'),
    ],
    "320_dockerfile_pipefail": [
        ('SHELL ["/bin/bash", "-o", "pipefail", "-c"]\n', ""),
        ('"-o", "pipefail", ', ""),
        ('["/bin/bash", ', '["/bin/sh", '),
        ("curl -fsSL", "curl -sSL"),
        ("helm-v{helm}", "helm-v3.0.0"),
        ("-C /usr/local/bin", "-C /opt"),
        (" linux-amd64/helm\n", "\n"),
        ("ca-certificates curl", "ca-certificates wget"),
        ('ENTRYPOINT ["deploy.sh"]', "ENTRYPOINT deploy.sh"),
        (
            "SHELL",
            "RUN curl -fsSL https://example.com/x.tar.gz | tar -xz\nSHELL",
        ),
    ],
    "321_dockerfile_cache_mount": [
        (f"--mount=type=cache,target=/root/.cache/pip {BS}\n    ", ""),
        ("target=/root/.cache/pip", "target=/tmp/pip"),
        ("type=cache", "type=tmpfs"),
        ("pip install -r", "pip install --no-cache-dir -r"),
        ("COPY requirements.txt .\n", ""),
        ("COPY app.py .\n", ""),
        ('"--host", "0.0.0.0"', '"--host", "127.0.0.1"'),
    ],
    "322_dockerfile_secret_mount": [
        (f"--mount=type=secret,id=pip_index_url,env=PIP_INDEX_URL {BS}\n    ", ""),
        ("id=pip_index_url", "id=token"),
        ("env=PIP_INDEX_URL", "target=/root/.netrc"),
        ("WORKDIR /app", "ARG PIP_INDEX_URL\nWORKDIR /app"),
        (
            "WORKDIR /app",
            "ENV PIP_INDEX_URL=https://pypi.acme.internal/simple\nWORKDIR /app",
        ),
        ("COPY requirements.txt .", "COPY requirements.txt pip.conf ./"),
        (
            "pip install --no-cache-dir -r",
            "PIP_INDEX_URL=$TOKEN pip install --no-cache-dir -r",
        ),
        ("COPY requirements.txt .\n", ""),
        ('"--port", "{port}"]', '"--port", "1"]'),
    ],
    "323_dockerfile_multistage_java": [
        ("maven:3.9-eclipse-temurin-{java}", "maven:3.9-eclipse-temurin-11"),
        ("eclipse-temurin:{java}-jre", "eclipse-temurin:{java}-jdk"),
        ("eclipse-temurin:{java}-jre", "maven:3.9-eclipse-temurin-{java}"),
        ("RUN mvn -B dependency:go-offline\n", ""),
        (
            "COPY pom.xml .\nRUN mvn -B dependency:go-offline\nCOPY src ./src",
            "COPY pom.xml .\nCOPY src ./src\nRUN mvn -B dependency:go-offline",
        ),
        ("COPY src ./src", "COPY . ."),
        ("mvn -B package", "mvn package"),
        (" AS build", ""),
        ("WORKDIR /app\n", "WORKDIR /app\nCOPY pom.xml .\n"),
        ("orders-1.0.0.jar app.jar", "orders-1.0.0.jar /opt/app.jar"),
        ('"app.jar"]', '"orders.jar"]'),
        ("ENV PORT={port}", "ENV PORT=1"),
        ("EXPOSE {port}", "EXPOSE 80"),
    ],
}
SEEDS = (0, 1, 2)

pytestmark = pytest.mark.skipif(
    tools.installed(tools.HADOLINT) is None,
    reason="hadolint is not installed: run `drillion doctor --fetch`",
)


def _docker_tasks():
    return {
        slug: meta
        for slug, meta in catalogue.tasks().items()
        if meta.get("kind") == catalogue.DOCKER
    }


def _grade(meta, brief, text):
    """The real child, grading `text` as the learner's Dockerfile. It has to sit under
    tasks/, the one tree the sandbox reads, and a unique name keeps parallel workers apart."""
    path = meta["dir"] / f"_test_{uuid.uuid4().hex}.Dockerfile"
    path.write_text(text, encoding="utf-8")
    try:
        passed, diagnostics, *_ = runner.run_manifest(
            meta, brief, learner=path, **kinds.of(meta).extra(meta)
        )
    finally:
        path.unlink()
    return passed, diagnostics


def test_every_docker_task_has_its_rules_listed():
    assert set(_docker_tasks()) == set(BREAKS)


@pytest.mark.parametrize("slug", sorted(BREAKS))
@pytest.mark.parametrize("seed", SEEDS)
def test_the_answer_key_passes(slug, seed):
    meta = _docker_tasks()[slug]
    brief = manifest.generate_brief(meta, seed)
    assert _grade(meta, brief, kinds.of(meta).answer_key(meta, brief)) == (True, [])


def _filled(part, brief):
    """A row with the brief's values in it; `${NAME}` is Docker's and stays."""
    for key, value in brief.items():
        part = part.replace(f"{{{key}}}", str(value))
    return part


@pytest.mark.parametrize(
    ("slug", "row"),
    [
        pytest.param(slug, row, id=f"{slug[:3]}-{i}")
        for slug, rows in sorted(BREAKS.items())
        for i, row in enumerate(rows)
    ],
)
def test_every_broken_rule_fails(slug, row):
    meta = _docker_tasks()[slug]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    old, new = (_filled(part, brief) for part in row)
    assert old in key, (slug, old)
    passed, diagnostics = _grade(meta, brief, key.replace(old, new))
    assert not passed and diagnostics, (slug, old)


def test_a_hadolint_finding_names_the_line_and_cannot_be_silenced():
    meta = _docker_tasks()["289_dockerfile_first_image"]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    shell = key.replace(
        'CMD ["python", "app.py"]', "# hadolint ignore=DL3025\nCMD python app.py"
    )
    passed, diagnostics = _grade(meta, brief, shell)
    assert not passed
    assert diagnostics[0]["file"] == "Dockerfile" and diagnostics[0]["line"] == 7
    assert "(DL3025)" in diagnostics[0]["message"]


def test_a_copy_of_a_file_the_context_lacks_is_named():
    meta = _docker_tasks()["289_dockerfile_first_image"]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    passed, diagnostics = _grade(meta, brief, key.replace("app.py .", "src/ ."))
    assert not passed
    assert diagnostics[0]["line"] == 3 and "`src/`" in diagnostics[0]["message"]
    assert "`app.py`" in diagnostics[0]["message"], "it says what the context does hold"


def test_compiled_python_in_a_context_is_neither_shown_nor_fingerprinted(tmp_path):
    """The image compiles every .py it ships, a context's app.py included."""
    meta = {**_docker_tasks()["289_dockerfile_first_image"]}
    shutil.copytree(meta["dir"], tmp_path / "task")
    meta["dir"] = tmp_path / "task"
    before = manifest.grader_revision(meta)
    cache = meta["dir"] / "context" / "__pycache__"
    cache.mkdir()
    (cache / "app.cpython-314.pyc").write_bytes(b"\xb2\x00")
    assert [f["path"] for f in kinds.of(meta).chart(meta)] == ["app.py"]
    assert manifest.grader_revision(meta) == before


def test_an_empty_file_is_refused_in_the_files_own_name():
    meta = _docker_tasks()["289_dockerfile_first_image"]
    passed, diagnostics = _grade(meta, manifest.generate_brief(meta, 0), "\n")
    assert not passed
    assert diagnostics == [
        {
            "path": None,
            "message": "Dockerfile is empty: write it before submitting",
            "file": "Dockerfile",
        }
    ]


def _parse(text):
    """The child's parser, run here on its own."""
    return grading.dockerfile_stages(grading.dockerfile_steps(text))


def test_the_parser_reads_a_dockerfile_as_the_builder_does():
    stages = _parse(
        "ARG V=1\n"
        "# a comment\n"
        "FROM golang:1.25 AS build\n"
        "RUN apt-get update \\\n"
        "# a comment inside a continuation is dropped\n"
        "    && apt-get install -y git\n"
        "COPY --from=x --chown=1:1 a b /dst/\n"
        "RUN <<EOF\n"
        "echo FROM nothing\n"
        "EOF\n"
        'CMD ["/app", "--flag"]\n'
        "FROM scratch\n"
        "ENTRYPOINT /app\n"
    )
    assert [(s["base"], s["name"], s["line"]) for s in stages] == [
        ("golang:1.25", "build", 3),
        ("scratch", None, 12),
    ]
    assert [s["cmd"] for s in stages[0]["globals"]] == ["ARG"]
    run, copy, heredoc, cmd = stages[0]["steps"]
    assert run["line"] == 4 and run["words"][-2:] == ["-y", "git"]
    assert "comment" not in run["args"]
    assert copy["flags"] == {"from": "x", "chown": "1:1"}
    assert copy["words"] == ["a", "b", "/dst/"]
    assert heredoc["line"] == 8 and "echo FROM nothing" in heredoc["args"]
    assert cmd["exec"] == ["/app", "--flag"] and cmd["line"] == 11
    assert stages[1]["steps"][0]["exec"] is None
    assert stages[0].all("RUN") == [run, heredoc] and stages[1].all("RUN") == []


def test_a_sitting_through_the_api_shows_the_context(monkeypatch):
    """What the page is given and sends back, from an empty Dockerfile to a pass."""
    slug = "296_dockerfile_multistage_go"
    monkeypatch.setenv("DRILLION_TOOLS_DIR", str(tools.tools_dir()))
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_docker_")), settings.root
    shutil.copytree(settings.tasks_dir / slug, tmp / "tasks" / slug)
    settings.root = tmp

    async def flow(api):
        opened = (await api.post(f"/api/task/{slug}/open")).json()
        assert opened["code"] == "" and opened["meta"]["edits"] == "Dockerfile"
        assert [f["path"] for f in opened["chart"]] == ["go.mod", "main.go"]
        meta = catalogue.tasks()[slug]
        key = kinds.of(meta).answer_key(meta, state.load()["open"][slug]["brief"])

        wrong = (
            await api.post(
                f"/api/task/{slug}/run",
                json={
                    "code": key.replace(":nonroot", ":latest"),
                    "etag": opened["etag"],
                    "submit": False,
                },
            )
        ).json()
        assert not wrong["passed"] and wrong["diagnostics"][0]["file"] == "Dockerfile"
        assert wrong["diagnostics"][0]["line"] == 7

        done = (
            await api.post(
                f"/api/task/{slug}/run",
                json={"code": key, "etag": wrong["etag"], "submit": True},
            )
        ).json()
        assert done["passed"] and done["graded"], done
        after = (await api.get(f"/api/task/{slug}")).json()
        assert after["code"] == ""
        assert after["archive"][-1]["revision"].startswith("d1:")
        assert after["archive"][-1]["hadolint"] == tools.HADOLINT_VERSION

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as api:
            await flow(api)

    try:
        asyncio.run(run())
    finally:
        settings.root = keep
        shutil.rmtree(tmp)
