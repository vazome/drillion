"""The language server bridge: the framing, the root swap, and the ways it ends.

Every test drives a stand-in for `basedpyright-langserver`, because what is worth pinning
here is the bridge's own behaviour when the other end misbehaves — not the type checker's."""

import asyncio
import json
import sys

import pytest
from fastapi import WebSocketDisconnect

from drillion import lsp
from drillion.settings import settings


class FakeWS:
    """A socket that hands over `script` and then hangs up, as a closed tab does.

    The bridge ends the moment either direction finishes, so a socket that hangs up at once
    would close before the server got a word in. `expect` holds it open until that many
    replies have come back."""

    def __init__(self, script=(), expect=0):
        self.script, self.sent, self.expect = list(script), [], expect

    async def receive_text(self):
        if self.script:
            return self.script.pop(0)
        while len(self.sent) < self.expect:
            await asyncio.sleep(0.01)
        raise WebSocketDisconnect(1000, "")

    async def send_text(self, text):
        self.sent.append(text)


def server(code):
    return (sys.executable, "-c", code)


def run(ws, code, timeout=20):
    """One bridge against one stand-in server. Returns when the bridge does."""
    lsp.SERVER = server(code)
    asyncio.run(asyncio.wait_for(lsp.bridge(ws), timeout))
    return ws


def test_the_root_is_swapped_for_the_real_tasks_directory():
    """The page sends a placeholder; the server must be told where the tasks actually are."""
    sent = json.loads(
        lsp._rooted(
            json.dumps(
                {"method": "initialize", "params": {"rootUri": "file:///workspace"}}
            ).encode()
        )
    )
    assert sent["params"]["rootUri"] == settings.tasks_dir.as_uri()
    assert sent["params"]["workspaceFolders"][0]["uri"] == settings.tasks_dir.as_uri()


def test_only_initialize_is_rewritten():
    """Every other message is the learner's traffic and must go through untouched."""
    original = json.dumps(
        {"method": "textDocument/didOpen", "params": {"x": 1}}
    ).encode()
    assert lsp._rooted(original) is original
    assert lsp._rooted(b"not json at all") == b"not json at all"


def test_a_framed_reply_reaches_the_page_unframed():
    """The socket carries bare JSON-RPC; the headers are the subprocess's business."""
    ws = run(
        FakeWS(expect=1),
        "import sys; body = b'{\"id\":1}';"
        'sys.stdout.buffer.write(b"Content-Length: %d\\r\\n\\r\\n" % len(body) + body);'
        "sys.stdout.buffer.flush(); import time; time.sleep(5)",
    )
    assert ws.sent == ['{"id":1}']


def test_the_page_hanging_up_ends_the_bridge():
    assert run(FakeWS(), "import time; time.sleep(30)").sent == []


def test_the_server_exiting_first_is_not_an_error():
    """terminate() on a process that has already gone raises, so the bridge must check."""
    assert run(FakeWS(['{"jsonrpc":"2.0"}']), "pass").sent == []


def test_a_half_written_message_does_not_hang_the_bridge():
    ws = run(
        FakeWS(),
        'import sys; sys.stdout.write("Content-Length: 99\\r\\n\\r\\n{partial"); sys.stdout.flush()',
    )
    assert ws.sent == []


def test_a_server_that_cannot_start_is_not_swallowed():
    """A missing basedpyright is a broken install, and must not look like a quiet editor."""
    lsp.SERVER = ("drillion-no-such-language-server",)
    with pytest.raises(FileNotFoundError):
        asyncio.run(lsp.bridge(FakeWS()))
