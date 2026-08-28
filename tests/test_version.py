"""One number, three readers. The version is declared once, in pyproject.toml;
the CLI, the health endpoint and the installed metadata have to agree."""

import asyncio
import tomllib
from importlib.metadata import version
from pathlib import Path

import httpx
import pytest

import drillion
from drillion.api import app
from drillion.cli import main


def _health():
    """The same ASGI drive tests/test_api.py uses: 127.0.0.1 is a host the app trusts."""

    async def get():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as client:
            return (await client.get("/api/health")).json()

    return asyncio.run(get())


def test_cli_health_and_metadata_agree(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    installed = version("drillion")
    assert capsys.readouterr().out.strip() == f"drillion {installed}"
    assert drillion.__version__ == installed
    assert _health()["version"] == installed


def test_pyproject_is_the_only_declaration():
    """A stale editable install is the drift this catches: bump pyproject and the
    installed metadata is behind until the next `uv sync`."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"][
        "version"
    ]
    assert declared == version("drillion")
