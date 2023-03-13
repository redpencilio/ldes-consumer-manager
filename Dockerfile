FROM semtech/mu-python-template:2.0.0-beta.1
LABEL org.opencontainers.image.authors="info@redpencil.io"

ENV DOCKER_HOST "unix://var/run/docker.sock"
ENV CONSUMER_IMAGE "redpencil/ldes-consumer-service:feature=stop-on-errors"


