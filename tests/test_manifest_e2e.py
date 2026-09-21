"""One manifest sitting, through the API, from an empty file to a reset one.

The phase gate. Every other manifest test reaches for a seam; this one only knows the
endpoints a browser calls, so it fails when the pieces are each right and do not fit.

Two graders run the same flow. `stub` is the stand-in the rest of the suite uses, and it
runs today. `real` is the pinned binary, and it skips until the release gate fills the pins.
Until then this proves drillion agrees with drillion's idea of kubeconform, which is worth
having and is not the same as agreeing with kubeconform.
"""

import asyncio
import os
import shutil

import httpx
import pytest

from drillion import catalogue, manifest, state, tools
from drillion.api import app
from drillion.settings import settings
from tests.fixtures import tasks_root
from tests.fixtures_manifest import fixture_task, stub_kubeconform

SLUG = "271_fixture"


@pytest.fixture
def fixture_root():
    tmp = tasks_root(**{SLUG: fixture_task()})
    keep = settings.root
    # A verified grader is found under the root, and this swaps the root for a throwaway.
    # Without carrying it across, `real` skips on the very machine that has one, which is
    # how the release gate could be passed and its test still never run.
    if (graders := keep / "tools").is_dir():
        shutil.copytree(graders, tmp / "tools")
    settings.root = tmp
    yield tmp
    settings.root = keep
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def stub(fixture_root, monkeypatch):
    if os.name == "nt":
        pytest.skip("the stand-in is a shebang script, so it needs a posix exec")
    path = stub_kubeconform(fixture_root)
    monkeypatch.setattr(tools, "installed", lambda name: path)
    return fixture_root


@pytest.fixture
def real(fixture_root):
    """The same flow against the pinned binary, for a root that has fetched one."""
    if tools.installed(tools.KUBECONFORM) is None:
        pytest.skip("kubeconform is not installed: run `drillion doctor --fetch`")
    return fixture_root


def _drive(flow):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as api:
            await flow(api)

    asyncio.run(run())


async def _sitting(api):
    """Open one, and answer it with the reference rendered against its own brief."""
    opened = (await api.post(f"/api/task/{SLUG}/open")).json()
    assert opened["code"] == "", "a manifest task opens empty"
    assert "{name}" not in opened["spec_md"], "the brief is rendered, not templated"

    wrong = (
        await api.post(
            f"/api/task/{SLUG}/run",
            json={
                "code": "kind: Deployment\n",
                "etag": opened["etag"],
                "submit": False,
            },
        )
    ).json()
    assert not wrong["passed"], wrong
    # what the page draws its Result panel from: fields and sentences, never parsed text
    assert wrong["diagnostics"], wrong
    assert all({"path", "message"} == set(d) for d in wrong["diagnostics"]), wrong
    assert wrong["case"] is None, "a manifest run has no generated-arguments case"

    meta = catalogue.tasks()[SLUG]
    brief = state.load()["open"][SLUG]["brief"]
    correct = manifest.render_solution(meta, brief)
    done = (
        await api.post(
            f"/api/task/{SLUG}/run",
            json={"code": correct, "etag": wrong["etag"], "submit": True},
        )
    ).json()
    assert done["passed"] and done["graded"] and done["grade"], done
    return meta, done


def _assert_closed(api_json, meta):
    """A passed sitting leaves the file empty and the grader it met in the archive."""
    assert (settings.tasks_dir / SLUG / "task.yaml").read_text(encoding="utf-8") == ""
    assert api_json["code"] == ""
    revision = api_json["archive"][-1]["revision"]
    assert revision == manifest.fingerprint(meta), "the archive records what judged it"
    assert revision.startswith("m1:"), revision


def test_a_sitting_goes_from_empty_to_passed_to_reset(stub):
    async def flow(api):
        meta, done = await _sitting(api)
        assert done["reference"], "passing is what opens the reference"
        after = (await api.get(f"/api/task/{SLUG}")).json()
        _assert_closed(after, meta)

    _drive(flow)


def test_the_same_flow_against_the_real_kubeconform(real):
    """The release gate. Skipped while the pins are empty, and a skipped gate proves
    nothing: filling them is what makes this the phase 1 gate rather than a reminder."""

    async def flow(api):
        meta, _ = await _sitting(api)
        after = (await api.get(f"/api/task/{SLUG}")).json()
        _assert_closed(after, meta)

    _drive(flow)


def test_two_sittings_ask_for_different_things(stub):
    """The whole point: the answer cannot be pasted back."""

    async def flow(api):
        seen = set()
        for _ in range(12):
            opened = (await api.post(f"/api/task/{SLUG}/open")).json()
            seen.add(opened["spec_md"])
            await api.post(f"/api/task/{SLUG}/abandon", json={"etag": opened["etag"]})
        assert len(seen) > 1, "every sitting asked for the same thing"

    _drive(flow)
