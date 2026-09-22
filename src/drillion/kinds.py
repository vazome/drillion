"""The learner's own text, whatever kind of task it lives in.

A Python task's artifact is the region above the marker in `task.py`; a manifest task's is
the whole of `task.yaml`. Everything that reads, writes, resets, archives or fingerprints
a learner's work asks a kind rather than calling `region` directly."""

import ast
import hashlib
import logging

import yaml

from . import region
from .catalogue import DOCKER, HELM, MANIFEST, PYTHON, solution
from .region import Invalid, _solve

__all__ = ["Invalid", "of"]

log = logging.getLogger(__name__)

# The seed a self-check asks its questions with, shared with `doctor` so that a task which
# renders for one and fails the other is not the seed's doing.
SELFCHECK_SEED = 1


def _reference_call(body):
    """solve()'s own signature, wired straight to the reference answer."""
    fn = _solve(ast.parse(body))
    a = fn.args
    args = [p.arg for p in a.posonlyargs + a.args]
    args += [f"*{a.vararg.arg}"] if a.vararg else []
    args += [f"{p.arg}={p.arg}" for p in a.kwonlyargs]
    args += [f"**{a.kwarg.arg}"] if a.kwarg else []
    stubbed = region.stub(body)
    return (
        stubbed[: stubbed.rindex("raise NotImplementedError")]
        + f"return _reference({', '.join(args)})"
    )


class _Python:
    """The original artifact: a region inside a file it shares with the grader."""

    name = PYTHON
    filename = "task.py"
    language = "python"

    def path(self, meta):
        return meta["dir"] / self.filename

    def body(self, src):
        return region.cut(src).body

    def compose(self, src, body):
        return region.splice(src, body)

    def validate(self, edited, src):
        return region.validate(edited, src)

    def empty(self, src):
        return region.splice(src, region.stub(region.cut(src).body))

    def etag(self, src):
        return region.etag(src)

    def has_given(self, body):
        """True when the region has code above solve() that the learner must keep."""
        return region.has_given(body)

    def opening(self, meta, seed):
        """Extra state an attempt on this kind carries. A python sitting needs none: its
        cases come from the seed at grading time, not from anything stored."""
        return {}

    def spec(self, meta, o):
        """The guidance this sitting shows. A python task's is the README as written."""
        return meta["spec_md"]

    def chart(self, meta):
        return []

    def reference(self, meta, o):
        from . import attempts

        return attempts.solution_text(meta["path"])

    def revision(self, meta, src):
        return region.revision(src)

    def provenance(self, o):
        """What a pass archives beside its grade: with the seed and the interpreter, the
        cases can be made again and the verdict reproduced."""
        from . import sandbox

        return {"seed": o["seed"], "python": sandbox.grading_python()}

    def grade(self, meta, o, src):
        """(passed, what the Result panel shows). The one place a kind's grader is chosen.

        pytest's own report is the python panel: its `task.py:12` is rewritten into the
        editor's coordinates, and the frame it failed on becomes the case."""
        from . import runner

        passed, out, case = runner.run_python(meta, o["seed"])
        summary = runner.summarise(out, region.bounds(src))
        return passed, {**summary, "case": case, "diagnostics": []}

    def selfcheck(self, meta):
        """({filename: text}, how to judge them). The files are written beside the task and
        deleted afterwards. A judge of None hands the `.py` files among them to the shared
        pytest batch: one pytest for the whole catalogue is the difference between seconds
        and minutes, and only this kind needs pytest at all.

        A python task proves itself by answering with `_reference`: the region is spliced
        so that `solve` forwards to it, and the task's own tests judge the result."""
        src = meta["path"].read_text(encoding="utf-8")
        body = _reference_call(region.cut(src).body)
        return {"_selfcheck.py": region.splice(src, body)}, None


class _Manifest:
    """The learner's artifact is the entire file: no marker, no machinery below it."""

    name = MANIFEST
    filename = "task.yaml"
    language = "yaml"
    suffix = ".yaml"

    def path(self, meta):
        return meta["dir"] / self.filename

    def body(self, src):
        return src

    def compose(self, src, body):
        return body

    def validate(self, edited, src):
        """Saving only asks that it parses. An empty file is a legal draft and a legal
        reset state, and so is a second document half typed; whether either is a legal
        *submission* is the grader's line, not this one, and it has better words for it."""
        try:
            list(yaml.safe_load_all(edited))
        except yaml.YAMLError as err:
            mark = getattr(err, "problem_mark", None)
            raise Invalid(
                getattr(err, "problem", None) or "this is not valid YAML",
                mark.line + 1 if mark else None,
            ) from None
        return edited

    def empty(self, src):
        return ""

    def etag(self, src):
        return hashlib.sha256(src.encode()).hexdigest()[:12]

    def has_given(self, body):
        # No code above solve() in a YAML file: nothing precedes what the learner writes.
        return False

    def opening(self, meta, seed):
        """The requirements for this sitting, generated once and then stored on it.

        Regenerating them from the seed on every render would let an upgraded grader change
        the question inside a live sitting, so the answer is written down here instead."""
        from . import manifest

        brief = manifest.generate_brief(meta, seed)
        return {
            "brief": brief,
            "spec_md": manifest.render(meta["spec_md"], brief),
            "brief_revision": manifest.grader_revision(meta),
        }

    def spec(self, meta, o):
        """The guidance this sitting shows. A rendered brief belongs to the sitting that was
        given it; with nothing open the README is served as written, placeholders and all,
        which is why `doctor` rejects a manifest whose Why or You get sections hold one."""
        return o["spec_md"] if o and "spec_md" in o else meta["spec_md"]

    def reference(self, meta, o):
        """The answer key for this sitting. A closed sitting has no stored brief to render
        one against, and an answer key that will not render is the task's bug, never the
        learner's: it must not cost them the pass that asked for it. `doctor` reports such a
        task, which is where it is meant to be caught."""
        from . import manifest

        if o is None or "brief" not in o:
            return None
        try:
            return self.answer_key(meta, o["brief"])
        except manifest.Rejected:
            log.exception(
                "%s: the solution does not render; run `drillion doctor`",
                meta["dir"].name,
            )
            return None

    def answer_key(self, meta, brief):
        from . import manifest

        return manifest.render_solution(meta, brief)

    def revision(self, meta, src):
        """What judged this pass, not merely what asked the question: the validator and the
        schemas decide a manifest verdict as much as `grade.py` does, so the archive records
        all three."""
        from . import manifest

        return manifest.fingerprint(meta)

    def provenance(self, o):
        """The sitting itself, so a finished one still shows the question it asked and the
        answer key for it, plus the validator and schema set that judged it."""
        from . import tools

        return {
            "seed": o["seed"],
            **{k: o[k] for k in ("brief", "spec_md", "brief_revision") if k in o},
            "validator": tools.pin_for(tools.KUBECONFORM).version,
            "kubernetes": tools.KUBERNETES_VERSION,
        }

    def grade(self, meta, o, src):
        """(passed, what the Result panel shows). The brief is the one the sitting was
        opened with, whatever grader revision is installed now. A sitting from before
        manifest grading has none, and its spec still holds raw placeholders, so grading it
        against anything now would grade requirements the learner was never shown. Refused
        with the way out instead.

        The panel is the diagnostics themselves: a field and what is wrong with it, as the
        validator and `check()` said it. `headline` is those messages in a line, for the
        parts of the page that show one whatever the kind."""
        from . import manifest, runner

        if "brief" not in o:
            raise manifest.Rejected(
                "this sitting opened before manifest grading: abandon it and start again"
            )
        # A grader upgraded under a live sitting still grades its stored brief; one that
        # can no longer read it is `run_manifest`'s Rejected, never the learner's failure.
        passed, diagnostics, report, rendered = runner.run_manifest(
            meta, o["brief"], **self.extra(meta)
        )
        return passed, {
            "headline": [d["message"] for d in diagnostics][:6],
            "output": report,
            "printed": "",
            "case": None,
            "diagnostics": diagnostics,
            "rendered": rendered,
        }

    def helm(self, meta):
        """What a Helm grader adds to the job; a manifest renders nothing first."""

    def extra(self, meta):
        """What this kind adds to the grading job, as `run_manifest`'s keywords."""
        return {"helm": self.helm(meta)}

    def chart(self, meta):
        """The read-only files the page shows beside the learner's: a Helm chart, or a
        Dockerfile's build context. A manifest has none."""
        from . import manifest

        return [
            {
                "path": p,
                "text": (manifest.shipped(meta) / p).read_text(encoding="utf-8"),
            }
            for p in manifest.chart_files(meta)
        ]

    def selfcheck(self, meta):
        """The same proof for the other kind: `solution.yaml` rendered against a real
        brief, then put through the validator and the `check()` that judge a learner's.

        `doctor` already asks whether the answer key renders. This asks the question only
        the grader can answer, which is whether the rendered key actually passes. It is
        judged one task at a time, by the same grader a submission meets."""
        from . import manifest, runner

        brief = manifest.generate_brief(meta, SELFCHECK_SEED)
        key = meta["dir"] / f"_selfcheck{self.suffix}"

        def judge():
            passed, diagnostics, *_ = runner.run_manifest(
                meta, brief, learner=key, **self.extra(meta)
            )
            return passed, diagnostics[0]["message"] if diagnostics else ""

        return {key.name: self.answer_key(meta, brief)}, judge


class _Helm(_Manifest):
    """A chart with one file missing: the learner's `task.yaml` is that file, at the chart
    path `edits` names. Everything else is the manifest kind's, with Helm in front of the
    validator: see `manifest.GRADE_SOURCE`."""

    name = HELM

    def validate(self, edited, src):
        """Nothing to parse on save: a template is not YAML until Helm renders it, and a
        values file's mistakes read better in Helm's words, on the run."""
        return edited

    def answer_key(self, meta, brief):
        """A values file is YAML with placeholders, as a manifest's key is. A template is
        the answer for any values, so it is served as written."""
        from . import manifest

        return manifest.render_solution(
            meta, brief, parse=meta["edits"] == "values.yaml"
        )

    def revision(self, meta, src):
        from . import manifest

        return manifest.fingerprint(meta, helm=True)

    def provenance(self, o):
        from . import tools

        return {**super().provenance(o), "helm": tools.pin_for(tools.HELM).version}

    def helm(self, meta):
        from . import manifest

        return manifest.helm_job(meta)


class _Docker(_Manifest):
    """A build context with its Dockerfile missing: the learner's `Dockerfile` is that
    file. Everything else is the manifest kind's, with hadolint standing in for the
    validator and nothing built: see `grade_docker` in `manifest.GRADE_SOURCE`."""

    name = DOCKER
    filename = "Dockerfile"
    language = "dockerfile"
    suffix = ".Dockerfile"

    def validate(self, edited, src):
        """Nothing to parse on save: hadolint says it better, on the run."""
        return edited

    def answer_key(self, meta, brief):
        """`solution.Dockerfile` with its placeholders filled in, as a README's are."""
        from . import manifest

        return manifest.render(solution(meta).read_text(encoding="utf-8"), brief)

    def revision(self, meta, src):
        from . import manifest

        return manifest.docker_fingerprint(meta)

    def provenance(self, o):
        from . import tools

        return {
            "seed": o["seed"],
            **{k: o[k] for k in ("brief", "spec_md", "brief_revision") if k in o},
            "hadolint": tools.pin_for(tools.HADOLINT).version,
        }

    def extra(self, meta):
        from . import manifest

        return {"docker": manifest.docker_job(meta)}


KINDS = {PYTHON: _Python(), MANIFEST: _Manifest(), HELM: _Helm(), DOCKER: _Docker()}


def of(meta):
    """The kind that owns this task's learner artifact. Raises KeyError on an unknown
    kind rather than guessing: the catalogue has already rejected those by name."""
    return KINDS[meta.get("kind", PYTHON)]
