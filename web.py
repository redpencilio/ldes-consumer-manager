# see https://github.com/mu-semtech/mu-python-template for more info
from helpers import logger
import docker
from config import MU_NETWORK,CONTAINER_LABEL,CONSUMER_IMAGE
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

@app.route("/ldes-consumers", methods = ['GET', 'POST'])
def ldes_consumers():
  if request.method == 'GET':
    consumers = list_containers()
    return jsonify(consumers)
  elif request.method == 'POST':
    content = request.json
    data = content["data"]
    attributes = data["attributes"]
    feed_url = attributes["ldes-endpoint"]
    dereference_members = attributes["dereference-members"]
    requests_per_minute = attributes["requests-per-minute"]
    replace_versions = attributes["replace-versions"]
    id = create_container(
      feed_url,
      {
        "LDES_DEREFERENCE_MEMBERS": dereference_members,
        "LDES_REQUESTS_PER_MINUTE": requests_per_minute,
        "REPLACE_VERSIONS": replace_versions
      }
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

