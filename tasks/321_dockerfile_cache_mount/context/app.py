"""An order service. uvicorn serves `app`; nothing here starts a server itself."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/orders")
def orders():
    return [{"id": 1, "status": "shipped"}]
