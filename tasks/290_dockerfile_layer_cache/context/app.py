"""An order service. gunicorn serves `app`; nothing here starts a server itself."""

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/orders")
def orders():
    return jsonify([{"id": 1, "status": "shipped"}])
