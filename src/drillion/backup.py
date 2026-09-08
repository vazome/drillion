"""A learner's practice data in one file they can keep: progress, plus the code they wrote.

Saved code travels as the learner's region rather than the whole task file, so a bundle
restored onto a different version of drillion is spliced into that version's machinery
instead of carrying a stale grader along with it. Progress travels as the same JSON the
domain already speaks, so a bundle outlives whatever database drillion stores it in."""

import io
import json
import logging
import zipfile
from datetime import datetime

from . import __version__, region, state
from .catalogue import tasks
from .settings import settings

FORMAT = 1
# What the Settings screen makes you type before an erase runs. It is deliberately a
# sentence rather than "yes": the point is that it cannot be reached by muscle memory.
PHRASE = "erase progress"
MANIFEST = "manifest.json"
PROGRESS = "progress.json"
REGIONS = "regions/"
log = logging.getLogger(__name__)


class Rejected(Exception):
    """The bundle is not one we can restore; live data was not touched."""


def bundle():
    """Progress and saved code as one zip, taken while no write is in flight."""
    with state.frozen() as st:
        progress = json.dumps(st, indent=2)
        saved = {
            slug: region.cut(meta["path"].read_text(encoding="utf-8")).body
            for slug, meta in tasks().items()
        }
    manifest = {
        "format": FORMAT,
        "drillion": __version__,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST, json.dumps(manifest, indent=2))
        zf.writestr(PROGRESS, progress)
        for slug, body in saved.items():
            zf.writestr(f"{REGIONS}{slug}.py", body)
    return buf.getvalue()


def _open(data):
    """Validate a bundle end to end, before any live data moves."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise Rejected("That file is not a drillion backup.") from exc
    with zf:
        try:
            manifest = json.loads(zf.read(MANIFEST))
        except (KeyError, ValueError) as exc:
            raise Rejected("That file is not a drillion backup.") from exc
        if not isinstance(manifest, dict):
            raise Rejected("That file is not a drillion backup.")
        if manifest.get("format") != FORMAT:
            raise Rejected(
                f"That backup is format {manifest.get('format')!r}; "
                f"this drillion reads format {FORMAT}."
            )
        try:
            progress = json.loads(zf.read(PROGRESS))
        except KeyError as exc:
            raise Rejected("That backup has no progress in it.") from exc
        except ValueError as exc:
            raise Rejected("The progress in that backup is damaged.") from exc
        saved = {
            name[len(REGIONS) : -len(".py")]: zf.read(name).decode("utf-8")
            for name in zf.namelist()
            if name.startswith(REGIONS) and name.endswith(".py")
        }
    try:
        # the same gate an imported state passes, so a bad shape is refused up front
        progress = state._checked(progress)
    except (state.Unreadable, state.TooNew) as exc:
        raise Rejected(str(exc)) from exc
    return manifest, progress, saved


def _counts(progress):
    return {key: len(progress.get(key, {})) for key in ("cards", "notes", "archive")}


def inspect(data):
    """What restoring this bundle would bring, and what it would replace."""
    manifest, progress, saved = _open(data)
    known = set(tasks())
    with state.frozen() as st:
        current = _counts(st)
    return {
        "created": manifest.get("created"),
        "drillion": manifest.get("drillion"),
        "brings": _counts(progress) | {"tasks": len(set(saved) & known)},
        "replaces": current,
        "unknown": sorted(set(saved) - known),
    }


def restore(data):
    """Replace progress and saved code from a bundle, or change nothing at all.

    Progress and every task file move inside one transaction, so a failure part-way
    leaves the previous state in place. What the restore is about to overwrite is written
    to a bundle of its own first, since the only safe undo is another backup. A task the
    bundle knows and this version does not is reported rather than dropped in silence."""
    _, progress, saved = _open(data)
    known = tasks()
    keep = settings.root / "backup-before-restore.zip"
    keep.write_bytes(bundle())
    log.info("wrote %s before restoring", keep)
    written, failed = 0, []
    with state.frozen(progress):
        for slug, body in saved.items():
            if slug not in known:
                continue
            path = known[slug]["path"]
            try:
                src = path.read_text(encoding="utf-8")
                region.write_region(path, region.validate(body, src))
                written += 1
            except (OSError, region.Invalid) as exc:
                log.warning("Could not restore the code for %s: %s", slug, exc)
                failed.append(slug)
    return {
        "brings": _counts(progress) | {"tasks": written},
        "unknown": sorted(set(saved) - set(known)),
        "failed": failed,
        "kept": str(keep),
    }


def erase():
    """Back to a first run: no progress at all, and every task emptied out.

    Emptying is what `abandon` does to one task, applied to all of them: the body of
    `solve` goes back to `raise NotImplementedError`. It is the file's own stub, so a
    signature the learner changed and saved stays changed.

    A backup of everything is written before the transaction opens, because the only undo
    for this is a restore. A task whose region no longer parses cannot be stubbed from its
    own text, so it is reported rather than left cleared-looking and unchanged."""
    keep = settings.root / "backup-before-reset.zip"
    keep.write_bytes(bundle())
    log.info("wrote %s before erasing", keep)
    cleared, failed = 0, []
    with state.frozen({}):
        for slug, meta in tasks().items():
            path = meta["path"]
            try:
                src = path.read_text(encoding="utf-8")
                body = region.cut(src).body
                stubbed = region.stub(body)
                if stubbed != body:
                    region.write_region(path, region.splice(src, stubbed))
                    cleared += 1
            except (OSError, SyntaxError, region.Invalid) as exc:
                log.warning("Could not clear the code for %s: %s", slug, exc)
                failed.append(slug)
    return {"cleared": cleared, "failed": failed, "kept": str(keep)}
