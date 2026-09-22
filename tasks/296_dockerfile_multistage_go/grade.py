"""What one sitting of 296 asks for, and what counts as having answered it.

hadolint refuses a COPY --from naming a stage that was never defined (DL3022). `check`
follows the binary: where the build writes it, what the final stage copies, and what it
runs."""

import posixpath

GOS = ["1.24", "1.25"]
NAMES = ["api", "gateway", "relay", "ingest", "notifier"]


def brief(r):
    return {"go": r.choice(GOS), "name": r.choice(NAMES)}


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


def _output(run):
    words = run["words"]
    for i, w in enumerate(words):
        if w == "-o" and i + 1 < len(words):
            return words[i + 1]
        if w.startswith("-o="):
            return w[3:]
    return None


def check(stages, b):
    assert len(stages) == 2, f"two stages, one to build and one to run: this file has {len(stages)}"
    build, final = stages
    assert build["base"] == f"golang:{b['go']}", (
        f"the build stage is FROM {build['base']!r}, and it should be 'golang:{b['go']}'"
    )
    assert build["name"], "name the build stage, `FROM golang:... AS build`, so the next one can copy from it"
    runs = [s for s in _all(build, "RUN") if "go" in s["words"] and "build" in s["words"]]
    assert len(runs) == 1, "build the binary with one `RUN go build` in the build stage"
    run = runs[0]
    env = " ".join(s["args"] for s in _all(build, "ENV"))
    assert "CGO_ENABLED=0" in run["words"] or "CGO_ENABLED=0" in env, (
        f"line {run['line']}: without CGO_ENABLED=0 the binary links against the build "
        "image's libc, which a static runtime image does not have"
    )
    out = _output(run)
    assert out and out.endswith(f"/{b['name']}"), (
        f"line {run['line']}: write the binary somewhere you can name, `-o /out/{b['name']}`"
    )
    allowed = final["base"] == "scratch" or final["base"].startswith("gcr.io/distroless/static")
    assert allowed, (
        f"the runtime stage is FROM {final['base']!r}: a static Go binary needs nothing under "
        "it, so `gcr.io/distroless/static-debian12:nonroot` or `scratch`"
    )
    assert not _all(final, "RUN"), (
        "the runtime stage has no shell to RUN anything with: do that work in the build stage"
    )
    copies = _all(final, "COPY")
    assert len(copies) == 1, "the runtime stage copies one thing, the binary"
    copy = copies[0]
    assert copy["flags"].get("from") == build["name"], (
        f"line {copy['line']}: copy the binary `--from={build['name']}`"
    )
    assert copy["words"][:-1] == [out], (
        f"line {copy['line']}: copy {out}, the binary line {run['line']} built, and nothing else"
    )
    dest = copy["words"][-1]
    path = posixpath.join(dest, b["name"]) if dest.endswith("/") else dest
    entry = _all(final, "ENTRYPOINT")
    assert len(entry) == 1 and entry[0]["exec"] == [path], (
        f"ENTRYPOINT should run the binary where line {copy['line']} put it: [\"{path}\"]"
    )
    users = _all(final, "USER")
    numeric = users and users[-1]["words"][0].split(":")[0] not in ("0", "root")
    assert final["base"].endswith(":nonroot") or numeric, (
        "run as a user that is not root: the distroless `:nonroot` tag, or `USER 65532` on scratch"
    )
