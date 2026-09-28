"""The Argo CD tasks through the real pipeline: the packaged Argo schemas behind the pinned
kubeconform, then `check()`. `test_graders.py` breaks each rule `check()` states; this is
what says a misspelt field never reaches it."""

import json
import uuid

import pytest

from drillion import catalogue, kinds, manifest, runner, tools

pytestmark = pytest.mark.skipif(
    tools.installed(tools.KUBECONFORM) is None,
    reason="kubeconform is not installed: run `drillion doctor --fetch`",
)

# (task, a line of its answer key, the same line misspelt, the field kubeconform names)
TYPOS = [
    ("358_argocd_automated_sync", "selfHeal: true", "selfHeel: true", "automated"),
    ("365_argocd_appset_list", "goTemplate: true", "goTemplates: true", ""),
    ("363_argocd_appproject", "sourceRepos:", "sourceRepo:", ""),
    ("367_argocd_rollout_canary", "setWeight:", "setWieght:", "steps"),
    ("368_argocd_canary_analysis", "successCondition:", "successCondtion:", "metrics"),
]


def _argo():
    return {
        slug: meta
        for slug, meta in catalogue.tasks().items()
        if meta.get("track") == "argocd"
    }


def _grade(meta, brief, text):
    """The real child, grading `text` as the learner's file. It has to sit under tasks/,
    the one tree the sandbox reads, and a unique name keeps parallel workers apart."""
    path = meta["dir"] / f"_test_{uuid.uuid4().hex}.yaml"
    path.write_text(text, encoding="utf-8")
    try:
        passed, diagnostics, *_ = runner.run_manifest(meta, brief, learner=path)
    finally:
        path.unlink()
    return passed, diagnostics


def test_the_packaged_argo_schemas_are_the_ones_recorded():
    recorded = json.loads((tools.SCHEMAS.parent / "manifest.json").read_text())["argo"]
    for kind in recorded["kinds"]:
        name = f"{kind.lower()}-argoproj-v1alpha1.json"
        assert (tools.SCHEMAS / name).is_file(), kind


@pytest.mark.parametrize("slug", sorted(_argo()))
def test_the_answer_key_passes_the_real_validator(slug):
    meta = _argo()[slug]
    brief = manifest.generate_brief(meta, 0)
    assert _grade(meta, brief, kinds.of(meta).answer_key(meta, brief)) == (True, [])


@pytest.mark.parametrize("slug, right, wrong, field", TYPOS)
def test_a_misspelt_argo_field_is_refused_by_the_schema(slug, right, wrong, field):
    meta = _argo()[slug]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    assert right in key
    passed, diagnostics = _grade(meta, brief, key.replace(right, wrong, 1))
    assert not passed
    said = diagnostics[0]
    assert wrong.split(":")[0] in said["message"], said
    assert field in (said["path"] or ""), said
