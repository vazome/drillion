FROM python:{python}-slim
RUN useradd --uid {uid} --no-create-home --shell /usr/sbin/nologin -l app
WORKDIR /app
COPY --chown={uid}:{uid} app.py .
ENV PORT={port}
EXPOSE {port}
USER {uid}
CMD ["python", "app.py"]
