import os
#CONSUMER_IMAGE = os.getenv("CONSUMER_IMAGE")
CONSUMER_IMAGE = "redpencil/ldes-consumer:feature-stop-on-errors"
MU_NETWORK = os.getenv("MU_NETWORK")
CONTAINER_LABEL="io.redpencil.ldes-consumer-manager"
DEFAULT_DEREFERENCE_MEMBERS = bool(os.getenv("DEFAULT_DEREFERENCE_MEMBERS", True))
DEFAULT_REQUESTS_PER_MINUTE = int(os.getenv("DEFAULT_REQUESTS_PER_MINUTE", 150))
DEFAULT_REPLACE_VERSIONS = bool(os.getenv("DEFAULT_REPLACE_VERSIONS", True))
