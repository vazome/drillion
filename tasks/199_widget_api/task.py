def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio

import httpx
from _lib import rng
from fastapi import FastAPI


def _reference():
    from fastapi.responses import JSONResponse

    class WidgetMissing(Exception):
        def __init__(self, widget_id):
            self.widget_id = widget_id

    app = FastAPI()
    app.state.widgets = {}

    @app.exception_handler(WidgetMissing)
    async def missing_widget(_request, error):
        return JSONResponse(status_code=404,
                            content={"detail": f"widget {error.widget_id} not found"})

    @app.get("/widgets/{widget_id}")
    async def widget(widget_id: int):
        if widget_id not in app.state.widgets:
            raise WidgetMissing(widget_id)
        return {"id": widget_id, "name": app.state.widgets[widget_id]}

    return app


async def _get(app, path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)
    return response.status_code, response.json()


def test_solve():
    app = solve()
    assert isinstance(app, FastAPI), "solve() must return a FastAPI app"
    custom = next((kind for kind in app.exception_handlers
                   if isinstance(kind, type) and kind.__name__ == "WidgetMissing"), None)
    assert custom is not None, "register a handler for your WidgetMissing exception"
    original_handler = app.exception_handlers[custom]
    caught = []

    async def record_handler(request, error):
        caught.append(error.widget_id)
        return await original_handler(request, error)

    app.exception_handlers[custom] = record_handler

    r = rng()
    widgets = {number: f"widget-{r.randint(10, 99)}" for number in r.sample(range(1, 20), 4)}
    app.state.widgets = widgets
    for widget_id, name in widgets.items():
        assert asyncio.run(_get(app, f"/widgets/{widget_id}")) == (
            200, {"id": widget_id, "name": name})
    missing = next(number for number in range(1, 30) if number not in widgets)
    assert asyncio.run(_get(app, f"/widgets/{missing}")) == (
        404, {"detail": f"widget {missing} not found"})
    assert caught == [missing], "the missing route must raise WidgetMissing"
    status, body = asyncio.run(_get(app, "/widgets/not-a-number"))
    assert status == 422 and "detail" in body
