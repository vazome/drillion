FROM python:{python}-slim
WORKDIR /app
COPY app.py .
ENV PORT={port}
EXPOSE {port}
CMD ["python", "app.py"]
