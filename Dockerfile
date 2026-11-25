FROM semtech/mu-python-template:feature-semantic-ai-fixes
LABEL org.opencontainers.image.authors="info@redpencil.io"

ENV DOCKER_HOST "unix://var/run/docker.sock"
ENV CONSUMER_IMAGE "redpencil/ldes-consumer-service:feature=stop-on-errors"


