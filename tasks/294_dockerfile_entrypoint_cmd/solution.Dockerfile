FROM python:{python}-slim
WORKDIR /app
COPY worker.py .
ENTRYPOINT ["python", "worker.py"]
CMD ["--queue", "{queue}", "--concurrency", "{concurrency}"]
