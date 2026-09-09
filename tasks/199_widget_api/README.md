---
title: FastAPI — translate a domain error into a response
difficulty: medium
tier: packages
minutes: 24
prereqs: [121, 164]
tags: [fastapi, user-defined-errors]
---
# FastAPI — translate a domain error into a response

*Raise a Python error in the domain path and let one handler own its HTTP form.*

## Read first
- [FastAPI handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — custom exception handlers
- [User-defined exceptions](https://devdocs.io/python~3.14/tutorial/errors#user-defined-exceptions) — small exception classes carrying context
- [JSONResponse](https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse) — explicit status and JSON content

## Why
A lookup function should say “widget missing” in domain language. If every route constructs its own 404, the response format spreads through the app. FastAPI can translate one custom exception consistently at the boundary.

## You get
Nothing is passed to `solve`; the grader fills the returned app's `app.state.widgets` dictionary before making requests.

## You return
A `FastAPI` app with a mutable dictionary at `app.state.widgets`.

## Rules
Inside `solve`:

1. Define `WidgetMissing(Exception)` and retain its `widget_id`.
2. Create the app and set `app.state.widgets = {}`.
3. Register an exception handler returning status `404` and `{"detail": "widget <id> not found"}`.
4. Add `GET /widgets/{widget_id}` with `widget_id: int`. Return `{"id": widget_id, "name": name}` when found; otherwise raise `WidgetMissing`.

Return the app. Leave invalid non-integer paths to FastAPI's own `422` validation.

## Hints
### Hint 1
The route raises the domain exception. The decorated handler is the only code that knows it becomes HTTP 404.
### Hint 2
Use `@app.exception_handler(WidgetMissing)` and return `JSONResponse(status_code=404, content=...)`.
### Hint 3
Use `@app.get("/widgets/{widget_id}")` on an async function. Look up `app.state.widgets`; raise when the integer key is absent.
