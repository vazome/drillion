"""Choose the CI checks affected by a commit range. Unknown input runs them all."""

import os
import subprocess
import tomllib
from pathlib import Path

CHECKS = ("docs", "film", "check", "web", "screens", "image")
FULL = set(CHECKS)
CODE = {"check", "web", "screens", "image"}
PROSE = {
    "README.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTEXT.md",
    "DESIGN.md",
    "SECURITY.md",
    "web/README.md",
    ".github/pull_request_template.md",
}
METADATA = ("description", "keywords", "classifiers", "urls")


def project_without_prose(ref):
    text = subprocess.check_output(["git", "show", f"{ref}:pyproject.toml"])
    data = tomllib.loads(text.decode())
    for key in METADATA:
        data["project"].pop(key, None)
    return data


def metadata_only(base, head):
    try:
        return project_without_prose(base) == project_without_prose(head)
    except Exception:  # noqa: BLE001
        # Any unreadable or unexpected metadata shape must select the full checks.
        return False


def checks_for(path, base, head):
    if path == "pyproject.toml":
        return {"docs"} if metadata_only(base, head) else CODE
    if path in {".github/workflows/ci.yml", ".github/scripts/ci-changes.py"}:
        return FULL
    if path.startswith("docs/film/"):
        return {"docs"} if path.endswith(".md") else {"film"}
    if (
        path in PROSE
        or path.startswith(("docs/", ".design-sync/"))
        and path.endswith(".md")
        or path.startswith(".github/ISSUE_TEMPLATE/")
    ):
        return {"docs"}
    if path.startswith("docs/images/") and path.endswith(
        (".png", ".jpg", ".svg", ".webp", ".avif")
    ):
        return set()
    if path.startswith("web/e2e/") or path == "web/playwright.config.ts":
        return {"web", "screens"}
    if path.startswith("web/"):
        return {"web", "screens", "image"}
    return CODE


def selected():
    base, head = os.environ.get("BASE"), os.environ.get("HEAD")
    if os.environ.get("EVENT_NAME") == "schedule" or not base or not head:
        return FULL
    try:
        # No rename detection: include both sides of a move. NULs preserve filenames.
        paths = subprocess.check_output(
            ["git", "diff", "--no-renames", "--name-only", "-z", base, head, "--"]
        ).split(b"\0")
    except subprocess.CalledProcessError:
        return FULL
    if paths == [b""]:
        return FULL
    result = set()
    for raw in paths:
        if raw:
            result.update(checks_for(os.fsdecode(raw), base, head))
    return result


def main():
    chosen = selected()
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        for name in CHECKS:
            print(f"{name}={'true' if name in chosen else 'false'}", file=output)
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as summary:
        print("CI checks: " + (", ".join(sorted(chosen)) or "none"), file=summary)


if __name__ == "__main__":
    main()
