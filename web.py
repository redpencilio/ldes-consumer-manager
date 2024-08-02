# see https://github.com/mu-semtech/mu-python-template for more info
from helpers import logger, query, update
from escape_helpers import sparql_escape_uri
import docker
import datetime
from string import Template
from config import (MU_NETWORK,CONTAINER_LABEL,CONSUMER_IMAGE,DEFAULT_DEREFERENCE_MEMBERS,
                   DEFAULT_REQUESTS_PER_MINUTE,DEFAULT_REPLACE_VERSIONS, CRON_PATTERN,
                   REMOVE_CONTAINERS_ON_DELETE)
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
        inserts = list(filter(lambda i:i['predicate']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', inserts))
        inserts = list(filter(lambda i:i['object']['value'] == 'http://rdfs.org/ns/void#Dataset', inserts))
        subjects = set(map(lambda i:i['subject']['value'], inserts))
        logger.info(f"Received {len(subjects)} new dataset (type) inserts through delta.")

        to_create = []

        for subject in subjects:
            _query = Template("""
SELECT * WHERE {
    $subject <http://purl.org/dc/terms/type> <http://vocabsearch.data.gift/dataset-types/LDES> ;
        <http://xmlns.com/foaf/0.1/page> ?feed ;
        <http://mu.semte.ch/vocabularies/ext/maxRequests> ?maxRequests .
}""").substitute(subject=sparql_escape_uri(subject))
            results = query(_query)['results']['bindings']
            logger.info(f"{len(results)} / {len(subjects)} received datasets are ldes-datasets.")
            for result in results:
                to_create.append((subject, result['feed']['value'], result['maxRequests']['value']))

    for entry in to_create:
      create_consumer_container(entry[1], dataset=entry[0], requests_per_minute=entry[2])


    deletes = content['deletes']
    deletes = list(filter(lambda i:i['predicate']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', deletes))
    deletes = list(filter(lambda i:i['object']['value'] == 'http://rdfs.org/ns/void#Dataset', deletes))
    subjects = set(map(lambda i:i['subject']['value'], deletes))

    to_delete = []

    for subject in subjects:
      _query = "SELECT * WHERE {<" + str(subject) + "> <http://mu.semte.ch/vocabularies/ext/datasetGraph> ?graph . }"
      results = query(_query)['results']['bindings']
      for result in results:
        to_delete.append(result['graph']['value'])

    for entry in to_delete:
      remove_consumer_container(entry)
    return ('', 204)

def create_consumer_container(feed_url, dereference_members=DEFAULT_DEREFERENCE_MEMBERS, requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE, replace_versions=DEFAULT_REPLACE_VERSIONS, dataset=None, cron_pattern=CRON_PATTERN):
    options = {
    "LDES_DEREFERENCE_MEMBERS": dereference_members,
    "LDES_REQUESTS_PER_MINUTE": requests_per_minute,
    "CRON_PATTERN": CRON_PATTERN,
    "REPLACE_VERSIONS": replace_versions
    }
    existing_containers = []
    if dataset is not None:
        options["DATASET_URL"] = dataset
        logger.info(f"Looking for existing ldes consumer containers for dataset {dataset} ...")
        existing_containers = list(filter(lambda i:i['attributes']['dataset'] == dataset, list_containers()['data']))

    if not existing_containers:
        logger.info(f"No ldes consumer container for dataset {dataset} yet. Creating one ...")
        id = create_container(
            feed_url,
            options
        )
        if dataset is not None:
            graph = id["attributes"]["graph"]
            _query_template = Template("""
INSERT DATA {
    GRAPH <http://mu.semte.ch/graphs/public> {
        $dataset <http://mu.semte.ch/vocabularies/ext/datasetGraph> $graph .
    }
}""")
            _query = _query_template.substitute(
                dataset=sparql_escape_uri(dataset),
                graph=sparql_escape_uri(graph)
            )
            update(_query)
        return jsonify({
            "type": "ldes-consumers",
            "id": id,
            "data": {
                "feed-url": feed_url,
                "dereference-members": dereference_members,
                "requests-per-minute": requests_per_minute,
                "replace-versions": replace_versions
            }
        })
    else:
        logger.info(f"Already {len(existing_containers)} ldes consumer containers existing for dataset {dataset}. Returning the first one ...")
        container = existing_containers[0]
        attributes = container['attributes']
        return jsonify({
            "type": "ldes-consumers",
            "id": container['id'],
            "data": {
                "feed-url": attributes['feed-url'],
                "dereference-members": attributes['dereference-members'],
                "requests-per-minute": attributes['requests-per-minute'],
                "replace-versions": attributes['replace-versions']
            }
        })

def remove_consumer_container(graph):
    print("Deleting container to graph: ", graph)
    containers = list(filter(lambda i:i['attributes']['graph'] == graph, list_containers()['data']))
    if len(containers):
        container = client.containers.list(filters = { "id": [containers[0]['id']]})
        if len(container):
            container[0].kill()
            if REMOVE_CONTAINERS_ON_DELETE:
                container[0].remove()
