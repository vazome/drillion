"""A git sitting's repository, and the git that builds and grades it."""

import pytest

from drillion import gitrepo, manifest


def test_the_version_is_the_numbers_git_prints(monkeypatch):
    gitrepo.version.cache_clear()
    monkeypatch.setattr(gitrepo, "_git_says", lambda: "git version 2.47.3\n")
    assert gitrepo.version() == "2.47.3"
    gitrepo.version.cache_clear()


def test_an_old_git_is_refused_with_the_floor(monkeypatch):
    monkeypatch.setattr(gitrepo, "version", lambda: "2.34.1")
    with pytest.raises(manifest.ToolMissing, match="2.40"):
        gitrepo.require()


def test_no_git_is_refused_with_the_install(monkeypatch):
    monkeypatch.setattr(gitrepo, "version", lambda: None)
    with pytest.raises(manifest.ToolMissing, match="git is not installed"):
        gitrepo.require()
