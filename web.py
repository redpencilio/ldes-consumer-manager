# see https://github.com/mu-semtech/mu-python-template for more info
from helpers import logger, query
import docker
from config import (MU_NETWORK,CONTAINER_LABEL,CONSUMER_IMAGE,DEFAULT_DEREFERENCE_MEMBERS,
                   DEFAULT_REQUESTS_PER_MINUTE,DEFAULT_REPLACE_VERSIONS, CRON_PATTERN)
from utils import create_container, list_containers
from flask import jsonify, request


def docker_is_up():
  try:
    client = docker.from_env()
    client.ping()
    return True
  except RuntimeError:
    return False

if MU_NETWORK is None or len(MU_NETWORK) == 0:
  raise Exception("MU_NETWORK is a required variable")

logger.info(f"Consumers will be added to network \"{MU_NETWORK}\"")
logger.info(f"filtering on containers with label {CONTAINER_LABEL}")

if docker_is_up():
  client = docker.from_env()
  logger.info(f"Pulling consumer image {CONSUMER_IMAGE}")
  client.images.pull(CONSUMER_IMAGE)
else:
  logger.warn("Could not reach docker daemon")

@app.route("/hello")
def hello():
  try:
    client.ping()
    return "Hello from the ldes-consumer manager, docker is responsive!"
  except RuntimeError:
    return "Hello from the ldes-consumer manager, docker is not responding!"

@app.route("/ldes-consumers", methods = ['GET'])
def ldes_consumers():
  consumers = list_containers()
  return jsonify(consumers)

@app.route("/ldes-consumers", methods = ['POST'])
def ldes_consumer_add():
  content = request.json
  data = content["data"]
  attributes = data["attributes"]
  feed_url = attributes["ldes-endpoint"]
  dereference_members = attributes["dereference-members"]
  requests_per_minute = attributes["requests-per-minute"]
  replace_versions = attributes["replace-versions"]

  return create_consumer_container(feed_url, dereference_members, requests_per_minute, replace_versions)

@app.route("/delta", methods = ['POST'])
def process_delta():
  for content in request.json:
    inserts = content['inserts']
    subjects = set(map(lambda i:i['subject']['value'], inserts))

    to_create = []

    for subject in subjects:
      _query = "SELECT ?feed ?type WHERE {<" + str(subject) + "> <http://purl.org/dc/terms/type> ?type ; <http://xmlns.com/foaf/0.1/page> ?feed . }"
      results = query(_query)['results']['bindings']
      for result in results:
          if result['type']['value'] == "http://vocabsearch.data.gift/dataset-types/LDES":
              to_create.append((subject, result['feed']['value']))

    for entry in to_create:
      create_consumer_container(entry[1], dataset=entry[0])
  return ('', 204)



def create_consumer_container(feed_url, dereference_members=DEFAULT_DEREFERENCE_MEMBERS, requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE, replace_versions=DEFAULT_REPLACE_VERSIONS, dataset=None, cron_pattern=CRON_PATTERN):
  options = {
    "LDES_DEREFERENCE_MEMBERS": dereference_members,
    "LDES_REQUESTS_PER_MINUTE": requests_per_minute,
    "CRON_PATTERN": CRON_PATTERN,
    "REPLACE_VERSIONS": replace_versions
  }
  if dataset is not None:
      options["DATASET_URL"] = dataset
  id = create_container(
    feed_url,
    options
  )
  return jsonify(
    {
      "type": "ldes-consumers",
      "id": id,
      "data": {
        "feed-url": feed_url,
        "dereference-members": dereference_members,
        "requests-per-minute": requests_per_minute,
        "replace-versions": replace_versions
      }
    }
  )

