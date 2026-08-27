"""The language server behind the editor: one basedpyright per open editor, framed both ways.

The page only ever holds the learner's region, so the region is the whole document the
server is given — a task's machinery never reaches the browser through here. Every region
is self-contained, so nothing is lost by withholding the rest."""

import asyncio
import json
import logging

from fastapi import WebSocketDisconnect

from .settings import settings

log = logging.getLogger(__name__)

SERVER = ("basedpyright-langserver", "--stdio")


def _rooted(message):
    """Point the server at the real tasks directory on the way past.

    The page has no business knowing filesystem paths, so it opens with a placeholder root
    and this swaps in the truth — which is also what lets a region's imports resolve."""
    try:
        data = json.loads(message)
    except ValueError:
        return message
    if data.get("method") != "initialize":
        return message
    root = settings.tasks_dir
    params = data.setdefault("params", {})
    params["rootUri"] = root.as_uri()
    params["rootPath"] = str(root)
    params["workspaceFolders"] = [{"uri": root.as_uri(), "name": "drillion"}]
    return json.dumps(data).encode()


async def _read(stdout):
    """One LSP message off the pipe: headers, a blank line, then Content-Length bytes."""
    length = 0
    while line := await stdout.readline():
        if line in (b"\r\n", b"\n"):
            break
        name, _, value = line.decode().partition(":")
        if name.strip().lower() == "content-length":
            length = int(value)
    return await stdout.readexactly(length) if length else None


async def _to_editor(stdout, ws):
    """Server to page: strip the framing, the socket carries bare JSON-RPC."""
    while message := await _read(stdout):
        await ws.send_text(message.decode())


async def _to_server(ws, stdin):
    """Page to server: add the framing back on."""
    while True:
        message = _rooted((await ws.receive_text()).encode())
        stdin.write(f"Content-Length: {len(message)}\r\n\r\n".encode() + message)
        await stdin.drain()


async def bridge(ws):
    """Pipe one editor's JSON-RPC to its own basedpyright until either end hangs up."""
    proc = await asyncio.create_subprocess_exec(
        *SERVER, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )
    pump = [
        asyncio.create_task(_to_editor(proc.stdout, ws)),
        asyncio.create_task(_to_server(ws, proc.stdin)),
    ]
    try:
        done, _ = await asyncio.wait(pump, return_when=asyncio.FIRST_COMPLETED)
        for task in done:  # closing the tab is not news; anything else is
            if (err := task.exception()) and not isinstance(err, WebSocketDisconnect):
                log.info("language server bridge closed: %r", err)
    finally:
        for task in pump:
            task.cancel()
        # the server exiting first is one of the ways we get here, and terminating a process
        # that has already gone raises rather than being a no-op
        if proc.returncode is None:
            proc.terminate()
        await proc.wait()
