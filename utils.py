from helpers import generate_uuid, logger
from config import CONSUMER_IMAGE, MU_NETWORK, CONTAINER_LABEL, COMPOSE_PROJECT
import docker

def create_container(endpoint, dataset_graph, options):
  environment_options = options if options else {}
  client = docker.from_env()
  environment_options["LDES_ENDPOINT_VIEW"] = endpoint
  dataset_uuid = generate_uuid()
  environment_options["MU_APPLICATION_GRAPH"] = dataset_graph if dataset_graph else f"http://datasets.vocabsearch.local/{dataset_uuid}"
  environment_options["LDES_STREAM"] = dataset_graph if dataset_graph else f"http://datasets.vocabsearch.local/{dataset_uuid}"
  environment_options["LOG_LEVEL"] = "debug"
  environment_options["INGEST_MODE"] = "MATERIALIZE"
  environment_options["SPARQL_BATCH_SIZE"] = "150"
  container_labels = [CONTAINER_LABEL]

  # Make consumers show up in same overview for docker-compose ps
  if COMPOSE_PROJECT:
    container_labels = {
      CONTAINER_LABEL: None,
      "com.docker.compose.project": COMPOSE_PROJECT
    }

  container = client.containers.run(
      CONSUMER_IMAGE,
      detach=True,
      environment=environment_options,
      network=MU_NETWORK,
      restart_policy = {"Name": "always" },
      labels=container_labels
  )
  return container_to_json_view(container)


def container_to_json_view(container):
    container_env = dict(x.split("=") for x in container.attrs["Config"]["Env"])
    view = {
        "id": container.attrs["Id"],
        "type": "ldes-consumer",
        "attributes": {
            "status": container.attrs["State"]["Status"],
            "feed-url": container_env["LDES_ENDPOINT_VIEW"],
            "requests-per-minute": container_env["LDES_REQUESTS_PER_MINUTE"],
            "replace-versions": container_env["REPLACE_VERSIONS"],
            "graph": container_env["MU_APPLICATION_GRAPH"],
            "dataset": container_env["DATASET_URL"]
        }
    }
    return view

def list_containers():
    client = docker.from_env()
    containers = client.containers.list(filters = { "label": [CONTAINER_LABEL]})
    results = map(container_to_json_view, containers)
    return {
        "links": {
            "self": "/ldes-consumers"
        },
        "data": list(results)
    }
