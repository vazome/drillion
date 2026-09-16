"""The learner's own text, whatever kind of task it lives in.

A Python task's artifact is the region above the marker in `task.py`; a manifest task's is
the whole of `task.yaml`. Everything that reads, writes, resets, archives or fingerprints
a learner's work asks a kind rather than calling `region` directly."""

from . import region
from .catalogue import PYTHON
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

        return runner.run_tests(self.path(meta), o["seed"])


KINDS = {PYTHON: _Python()}


def of(meta):
    """The kind that owns this task's learner artifact. Raises KeyError on an unknown
    kind rather than guessing: the catalogue has already rejected those by name."""
    return KINDS[meta.get("kind", PYTHON)]
