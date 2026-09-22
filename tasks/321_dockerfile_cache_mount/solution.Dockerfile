FROM python:{python}-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY app.py .
EXPOSE {port}
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{port}"]
