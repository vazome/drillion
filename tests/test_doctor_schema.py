"""Contribution checks use the same schema filenames as kubeconform."""

import json
import subprocess
import sys

import pytest

from drillion import doctor, manifest, tools
from tests.fixtures_manifest import stub_kubeconform


@pytest.mark.parametrize("quote", ['"', "'"])
def test_schema_accepts_quoted_api_version(tmp_path, quote):
    (tmp_path / "solution.yaml").write_text(
        f"apiVersion: {quote}apps/v1{quote}\nkind: Deployment\n", encoding="utf-8"
    )
    assert doctor._schema_rules({"dir": tmp_path}) == []


def test_schema_checks_indented_root_keys(tmp_path):
    (tmp_path / "solution.yaml").write_text(
        "  apiVersion: v1\n  kind: Unpackaged\n", encoding="utf-8"
    )
    reasons = doctor._schema_rules({"dir": tmp_path})
    assert any("no packaged schema for Unpackaged (v1)" in r for r in reasons)


@pytest.mark.parametrize(
    "kind, api, filename",
    [
        ("Deployment", "apps/v1", "deployment-apps-v1.json"),
        ("Service", "v1", "service-v1.json"),
        ("CronJob", "batch/v1", "cronjob-batch-v1.json"),
        ("Ingress", "networking.k8s.io/v1", "ingress-networking-v1.json"),
        ("Role", "rbac.authorization.k8s.io/v1", "role-rbac-v1.json"),
        (
            "CustomResourceDefinition",
            "apiextensions.k8s.io/v1",
            "customresourcedefinition-apiextensions-v1.json",
        ),
    ],
    ids=["deployment", "service", "cronjob", "ingress", "role", "crd"],
)
def test_schema_matches_kubeconform_filename(
    tmp_path, monkeypatch, kind, api, filename
):
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    (schemas / filename).write_text("{}", encoding="utf-8")
    monkeypatch.setattr(tools, "SCHEMAS", schemas)
    (tmp_path / "solution.yaml").write_text(
        f"apiVersion: {api}\nkind: {kind}\n", encoding="utf-8"
    )
    assert doctor._schema_rules({"dir": tmp_path}) == []
    (schemas / filename).unlink()
    assert any(
        f"no packaged schema for {kind} ({api})" in r
        for r in doctor._schema_rules({"dir": tmp_path})
    )


@pytest.mark.parametrize(
    "text",
    [
        "apiVersion: apps/v1\n",
        "metadata:\n  kind: Deployment\n",
        "metadata:\n  name: {name}-web\n",
        "- Deployment\n",
        "kind: null\n",
        "kind: 42\n",
    ],
    ids=["missing", "nested", "template", "sequence", "null", "number"],
)
def test_schema_reports_undetermined_kind(tmp_path, text):
    (tmp_path / "solution.yaml").write_text(text, encoding="utf-8")
    assert doctor._schema_rules({"dir": tmp_path}) == [
        "solution.yaml: cannot determine kind"
    ]


def test_schema_template_fallback_keeps_first_fields(tmp_path):
    (tmp_path / "solution.yaml").write_text(
        "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: {name}-web\n"
        "apiVersion: v1\nkind: Unpackaged\n",
        encoding="utf-8",
    )
    assert doctor._schema_rules({"dir": tmp_path}) == []


def test_schema_solution_read_is_bounded(tmp_path):
    (tmp_path / "solution.yaml").write_bytes(
        b"apiVersion: apps/v1\nkind: Deployment\n#"
        + b"x" * (manifest.MAX_SPEC_CHARS * 2)
        + b"\xff"
    )
    assert doctor._schema_rules({"dir": tmp_path}) == [
        f"solution.yaml: exceeds {manifest.MAX_SPEC_CHARS} characters"
    ]


def test_schema_solution_at_limit_is_allowed(tmp_path):
    text = "apiVersion: apps/v1\nkind: Deployment\n#"
    text += "x" * (manifest.MAX_SPEC_CHARS - len(text))
    (tmp_path / "solution.yaml").write_text(text, encoding="utf-8")
    assert doctor._schema_rules({"dir": tmp_path}) == []


def test_schema_reports_invalid_utf8(tmp_path):
    (tmp_path / "solution.yaml").write_bytes(b"kind: Deployment\n#\xff")
    assert doctor._schema_rules({"dir": tmp_path}) == [
        "solution.yaml: is not valid UTF-8"
    ]


def test_stub_missing_api_version_matches_validator(tmp_path):
    stub = stub_kubeconform(tmp_path)
    submission = tmp_path / "task.yaml"
    submission.write_text("kind: Deployment\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(stub),
            "-strict",
            "-kubernetes-version",
            tools.KUBERNETES_VERSION,
            "-schema-location",
            tools.schema_location(),
            "-output",
            "json",
            str(submission),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stderr
    assert json.loads(result.stdout)["resources"] == [
        {
            "filename": str(submission),
            "status": "statusError",
            "msg": "error while parsing: missing 'apiVersion' key",
        }
    ]


@pytest.mark.parametrize("api", ["null", "42", "[apps/v1]"])
def test_schema_reports_non_string_api_version(tmp_path, api):
    (tmp_path / "solution.yaml").write_text(
        f"apiVersion: {api}\nkind: Deployment\n", encoding="utf-8"
    )
    assert doctor._schema_rules({"dir": tmp_path}) == [
        "solution.yaml: cannot determine apiVersion"
    ]
