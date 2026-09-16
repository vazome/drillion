"""The learner's own text, whatever kind of task it lives in.

A Python task's artifact is the region above the marker in `task.py`; a manifest task's is
the whole of `task.yaml`. Everything that reads, writes, resets, archives or fingerprints
a learner's work asks a kind rather than calling `region` directly."""

import hashlib

import yaml

from . import region
from .catalogue import MANIFEST, PYTHON
from .region import Invalid

__all__ = ["Invalid", "of"]


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

    def marker_line(self, src):
        """Where the learner's region stops, so pytest's `task.py:12` can be rewritten
        into the editor's own coordinates."""
        return region.bounds(src)

    def opening(self, meta, seed):
        """Extra state an attempt on this kind carries. A python sitting needs none: its
        cases come from the seed at grading time, not from anything stored."""
        return {}

    def spec(self, meta, o):
        """The guidance this sitting shows. A python task's is the README as written."""
        return meta["spec_md"]

    def grade(self, meta, o):
        """(passed, pytest output, case). The one place a kind's grader is chosen."""
        from . import runner

        return runner.run_python(meta, o["seed"])


class _Manifest:
    """The learner's artifact is the entire file: no marker, no machinery below it."""

    name = MANIFEST
    filename = "task.yaml"
    language = "yaml"

    def path(self, meta):
        return meta["dir"] / self.filename

    def body(self, src):
        return src

    def compose(self, src, body):
        return body

    def validate(self, edited, src):
        """Saving only asks that it parses. An empty file is a legal draft and a legal
        reset state; whether it is a legal *submission* is the grader's line, not this one."""
        try:
            yaml.safe_load(edited)
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

    def marker_line(self, src):
        # No marker, and no .py path in the output to rewrite: the whole file is theirs.
        return 0

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

    def grade(self, meta, o):
        """(passed, pytest output, None). The brief is the one the sitting was opened
        with; a sitting from before manifest grading has none, and its spec still holds
        raw placeholders, so grading it against anything now would grade requirements the
        learner was never shown. Refused with the way out instead."""
        from . import manifest, runner

        if "brief" not in o:
            raise manifest.Rejected(
                "this sitting opened before manifest grading: abandon it and start again"
            )
        return runner.run_manifest(meta, o["brief"])


KINDS = {PYTHON: _Python(), MANIFEST: _Manifest()}


def of(meta):
    """The kind that owns this task's learner artifact. Raises KeyError on an unknown
    kind rather than guessing: the catalogue has already rejected those by name."""
    return KINDS[meta.get("kind", PYTHON)]
