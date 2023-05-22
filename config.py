import os
CONSUMER_IMAGE = os.getenv("CONSUMER_IMAGE") or "redpencil/ldes-consumer:feature-better-processing"
MU_NETWORK = os.getenv("MU_NETWORK")
CONTAINER_LABEL="io.redpencil.ldes-consumer-manager"
CRON_PATTERN=os.getenv("CRON_PATTERN", "* 0 * * * *")
DEFAULT_DEREFERENCE_MEMBERS = bool(os.getenv("DEFAULT_DEREFERENCE_MEMBERS", True))
DEFAULT_REQUESTS_PER_MINUTE = int(os.getenv("DEFAULT_REQUESTS_PER_MINUTE", 150))
DEFAULT_REPLACE_VERSIONS = bool(os.getenv("DEFAULT_REPLACE_VERSIONS", True))
