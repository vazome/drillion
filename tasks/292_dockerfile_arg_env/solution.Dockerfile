ARG PYTHON_VERSION={python}
FROM python:${{PYTHON_VERSION}}-slim
ARG APP_VERSION={version}
ENV APP_VERSION=${{APP_VERSION}} \
    LOG_LEVEL={level}
WORKDIR /app
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]
