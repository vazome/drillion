"""Every rule a Helm task shows the learner is one its grader enforces, through the real
pipeline: Helm, its lint, kubeconform and `check()`, in the sandbox, as a submission is.

For a values task a row changes one value in the answer key; for a template task it
replaces one piece of the template. Each row breaks exactly one displayed rule and must
fail. A rule with no row here is a rule a wrong answer can pass."""

import asyncio
import copy
import random
import shutil
import tempfile
import uuid
from pathlib import Path

import httpx
import pytest
import yaml

from drillion import catalogue, kinds, manifest, runner, state, tools
from drillion.api import app
from drillion.settings import settings

DROP = object()
WRONG, BIG = "zz-wrong", 99

# values tasks: (path into values.yaml, what to put there); DROP deletes the key
VALUES = {
    "279_helm_values_first": [
        (("replicaCount",), BIG),
        (("image", "repository"), WRONG),
        (("image", "tag"), 1.27),  # a number: the schema refuses it
        (("service", "port"), 1234),
        (("replicas",), 3),  # a key the chart does not read: the schema refuses it
    ],
    "280_helm_values_nodeport": [
        (("service", "type"), "ClusterIP"),
        (("service", "nodePort"), DROP),
        (("service", "nodePort"), 30001),
        (("service", "port"), 1234),
        (("replicaCount",), BIG),
    ],
    "281_helm_values_resources": [
        (("resources", "requests", "cpu"), "999m"),
        (("resources", "requests", "memory"), "1Mi"),
        (("resources", "limits", "cpu"), "1"),
        (("resources", "limits"), DROP),
        (("image",), WRONG),
    ],
    "282_helm_values_no_schema": [
        (("replicaCount",), DROP),  # the silent default: one replica renders
        (("image", "tag"), DROP),
        (("env", 0, "value"), WRONG),
        (("env", 2, "value"), True),  # unquoted: kubeconform refuses a boolean
        (("env", 3), {"name": "EXTRA", "value": "1"}),
    ],
    "283_helm_values_persistence": [
        (("persistence", "enabled"), False),
        (("persistence", "enabled"), "true"),  # a string: the schema refuses it
        (("persistence", "size"), "3Gi"),
        (("persistence", "storageClass"), DROP),
        (("image",), WRONG),
    ],
}

# template tasks: (what in the answer key, what to put instead)
TEMPLATES = {
    "284_helm_template_deployment": [
        ("replicas: {{ .Values.replicaCount }}", "replicas: 3"),
        ("  name: {{ .Release.Name }}", "  name: web"),
        ("{{ .Values.image.tag }}", "1.27"),
        (
            "      labels:\n        app: {{ .Release.Name }}",
            "      labels:\n        app: web",
        ),
    ],
    "285_helm_template_configmap": [
        ("{{ $value | quote }}", "{{ $value }}"),
        ("  name: {{ .Release.Name }}-config", "  name: config"),
        (
            (
                "  {{- range $key, $value := .Values.config }}\n"
                "  {{ $key }}: {{ $value | quote }}\n"
                "  {{- end }}"
            ),
            '  LOG_LEVEL: "info"',
        ),
    ],
    "286_helm_template_resources": [
        ("nindent 12", "nindent 10"),
        (
            "{{- toYaml .Values.resources | nindent 12 }}",
            "requests:\n              cpu: 100m",
        ),
        (  # the key rendered even when the value is empty
            (
                "      {{- with .Values.nodeSelector }}\n"
                "      nodeSelector:\n"
                "        {{- toYaml . | nindent 8 }}\n"
                "      {{- end }}"
            ),
            "      nodeSelector:\n        {{- toYaml .Values.nodeSelector | nindent 8 }}",
        ),
        ("  name: {{ .Release.Name }}", "  name: api"),
    ],
    "287_helm_template_service_toggle": [
        ("{{- if .Values.service.enabled }}", "{{- if true }}"),
        (' | default "ClusterIP"', ""),
        ("targetPort: 80", "targetPort: 8080"),
        ("    app: {{ .Release.Name }}", "    app: web"),
    ],
    "288_helm_template_secret": [
        ("username | b64enc | quote", "username | quote"),
        ("password | b64enc | quote", "password | quote | b64enc"),
        ("\ndata:", "\nstringData:"),
        ("  name: {{ .Release.Name }}-auth", "  name: auth"),
    ],
}
SEEDS = (0, 1)

pytestmark = pytest.mark.skipif(
    tools.installed(tools.HELM) is None or tools.installed(tools.KUBECONFORM) is None,
    reason="helm and kubeconform are not installed: run `drillion doctor --fetch`",
)


def _helm_tasks():
    return {
        slug: meta
        for slug, meta in catalogue.tasks().items()
        if meta.get("kind") == catalogue.HELM
    }


def _grade(meta, brief, text):
    """The real child, grading `text` as the learner's file. It has to sit under tasks/,
    the one tree the sandbox reads, and a unique name keeps parallel workers apart."""
    path = meta["dir"] / f"_test_{uuid.uuid4().hex}.yaml"
    path.write_text(text, encoding="utf-8")
    try:
        passed, diagnostics, *_ = runner.run_manifest(
            meta, brief, learner=path, helm=kinds.of(meta).helm(meta)
        )
    finally:
        path.unlink()
    return passed, diagnostics


def _set(values, path, value):
    values = copy.deepcopy(values)
    *parents, last = path
    node = values
    for step in parents:
        node = node[step]
    if value is DROP:
        del node[last]
    elif isinstance(node, list) and last == len(node):
        node.append(value)
    else:
        node[last] = value
    return values


def test_every_helm_task_has_its_rules_listed():
    assert set(_helm_tasks()) == set(VALUES) | set(TEMPLATES)


def test_every_template_task_renders_more_than_once():
    """One render cannot tell a template from a hardcoded manifest."""
    for slug in TEMPLATES:
        meta = _helm_tasks()[slug]
        assert meta["edits"].startswith("templates/")
        assert "def renders(" in (meta["dir"] / "grade.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("slug", sorted({**VALUES, **TEMPLATES}))
@pytest.mark.parametrize("seed", SEEDS)
def test_the_answer_key_passes(slug, seed):
    meta = _helm_tasks()[slug]
    brief = manifest.generate_brief(meta, seed)
    assert _grade(meta, brief, kinds.of(meta).answer_key(meta, brief)) == (True, [])


def _rows(table):
    """One test per broken rule, so a slow Helm run never queues behind another."""
    return [
        pytest.param(slug, row, id=f"{slug[:3]}-{i}")
        for slug, rows in sorted(table.items())
        for i, row in enumerate(rows)
    ]


@pytest.mark.parametrize(("slug", "row"), _rows(VALUES))
def test_every_broken_value_fails(slug, row):
    meta = _helm_tasks()[slug]
    brief = manifest.generate_brief(meta, SEEDS[0])
    values = yaml.safe_load(kinds.of(meta).answer_key(meta, brief))
    passed, diagnostics = _grade(
        meta, brief, yaml.safe_dump(_set(values, *row), sort_keys=False)
    )
    assert not passed and diagnostics, (slug, row)


@pytest.mark.parametrize(("slug", "row"), _rows(TEMPLATES))
def test_every_broken_template_fails(slug, row):
    meta = _helm_tasks()[slug]
    brief = manifest.generate_brief(meta, random.Random(slug).randrange(1000))
    key = kinds.of(meta).answer_key(meta, brief)
    old, new = row
    assert old in key, (slug, old)
    passed, diagnostics = _grade(meta, brief, key.replace(old, new))
    assert not passed and diagnostics, (slug, old)


def test_a_template_error_names_the_learners_file():
    meta = _helm_tasks()["284_helm_template_deployment"]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    passed, diagnostics = _grade(meta, brief, key.replace("}}", "}", 1))
    assert not passed
    assert diagnostics[0]["file"] == "templates/deployment.yaml"
    assert "templates/deployment.yaml:" in diagnostics[0]["message"]
    assert "web/" not in diagnostics[0]["message"], (
        "the chart name is not the learner's"
    )


def test_an_empty_file_is_refused_in_the_files_own_name():
    meta = _helm_tasks()["279_helm_values_first"]
    brief = manifest.generate_brief(meta, 0)
    passed, diagnostics = _grade(meta, brief, "\n")
    assert not passed
    assert diagnostics == [
        {
            "path": None,
            "message": "values.yaml is empty: write it before submitting",
            "file": "values.yaml",
        }
    ]


def test_a_sitting_through_the_api_shows_the_chart_and_the_render(monkeypatch):
    """What the page is given and sends back, from an empty template to a reset one."""
    slug = "284_helm_template_deployment"
    monkeypatch.setenv("DRILLION_TOOLS_DIR", str(tools.tools_dir()))
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_helm_")), settings.root
    shutil.copytree(settings.tasks_dir / slug, tmp / "tasks" / slug)
    settings.root = tmp

    async def flow(api):
        opened = (await api.post(f"/api/task/{slug}/open")).json()
        assert (
            opened["code"] == ""
            and opened["meta"]["edits"] == "templates/deployment.yaml"
        )
        assert [f["path"] for f in opened["chart"]] == ["Chart.yaml", "values.yaml"]
        meta = catalogue.tasks()[slug]
        key = kinds.of(meta).answer_key(meta, state.load()["open"][slug]["brief"])

        hardcoded = key.replace("{{ .Values.replicaCount }}", "1")
        wrong = (
            await api.post(
                f"/api/task/{slug}/run",
                json={"code": hardcoded, "etag": opened["etag"], "submit": False},
            )
        ).json()
        assert (
            not wrong["passed"]
            and "render 1 of 2" in wrong["diagnostics"][0]["message"]
        )
        assert "kind: Deployment" in wrong["rendered"], "the failing render is shown"

        done = (
            await api.post(
                f"/api/task/{slug}/run",
                json={"code": key, "etag": wrong["etag"], "submit": True},
            )
        ).json()
        assert done["passed"] and done["graded"], done
        assert done["reference"] == key, "a template's answer key is served as written"
        after = (await api.get(f"/api/task/{slug}")).json()
        assert after["code"] == ""
        assert after["archive"][-1]["revision"].startswith("h1:")
        assert after["archive"][-1]["helm"] == tools.HELM_VERSION

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
