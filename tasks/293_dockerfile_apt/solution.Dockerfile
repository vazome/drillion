FROM python:{python}-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backup.py .
CMD ["python", "backup.py"]
