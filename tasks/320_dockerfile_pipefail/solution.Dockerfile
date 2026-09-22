FROM debian:bookworm-slim
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://get.helm.sh/helm-v{helm}-linux-amd64.tar.gz \
    | tar -xz -C /usr/local/bin --strip-components=1 linux-amd64/helm
COPY deploy.sh /usr/local/bin/deploy.sh
ENTRYPOINT ["deploy.sh"]
