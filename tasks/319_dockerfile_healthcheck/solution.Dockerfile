FROM python:{python}-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE {port}
HEALTHCHECK --interval={interval}s --timeout=3s --start-period=10s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:{port}/health', timeout=2)"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{port}"]
