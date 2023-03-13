import os
#CONSUMER_IMAGE = os.getenv("CONSUMER_IMAGE")
CONSUMER_IMAGE = "redpencil/ldes-consumer:feature-stop-on-errors"
MU_NETWORK = os.getenv("MU_NETWORK")
CONTAINER_LABEL="io.redpencil.ldes-consumer-manager"
