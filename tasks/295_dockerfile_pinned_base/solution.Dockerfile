FROM python:{python}-slim@sha256:{digest}
ARG REVISION
LABEL org.opencontainers.image.source="{repo}" \
      org.opencontainers.image.revision="${{REVISION}}"
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
