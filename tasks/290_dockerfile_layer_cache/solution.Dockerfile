FROM python:{python}-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE {port}
CMD ["gunicorn", "--bind", "0.0.0.0:{port}", "app:app"]
