from fastapi import FastAPI

app = FastAPI()


@app.get("/orders")
def orders():
    return [{"id": 1, "status": "shipped"}]


@app.get("/health")
def health():
    return {"ok": True}
