# ldes-consumer-manager
This service provides an interface to manage [ldes-consumer-service](https://github.com/redpencilio/ldes-consumer-service) containers. It has irect access to the docker daemon, so do not expose it to the world.

## Usage

Add to docker-compose:
```yml
services:
  ldes-consumer-manager:
    image: redpencil/ldes-consumer-manager
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

## API:

### POST /ldes-consumers
```json
{
  "type": "ldes-consumers",
  "data": {
    "attributes": {
      "ldes-endpoint": "https://marineregions.org/feed",
      "dereference-members": true,
      "requests-per-minute": 150,
      "replace-versions": true
    }
  }
}
```

## Delta

This service can be configured to create consumers when LDES datasets get created, using the following delta configuration.
```js
  {
    match: {
      predicate: {
        type: 'uri',
        value: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
      },
      object: {
        type: 'uri',
        value: 'http://rdfs.org/ns/void#Dataset'
      }
    },
    callback: {
      url: 'http://ldes-consumer-manager/delta',
      method: 'POST'
    },
    options: {
      resourceFormat: 'v0.0.1',
      gracePeriod: 2500,
      ignoreFromSelf: true
    }
  }
```

## Environment variables

- `CRON_PATTERN` [string]: the cron pattern which the cronjob should use. (default: `* 0 * * * *`)
- `CONSUMER_IMAGE`: the image that should be used when creating consumers
- `DEFAULT_DEREFERENCE_MEMBERS`: whether to derefence the members (default: `True`)
- `DEFAULT_REQUESTS_PER_MINUTE`: number of requests per minute (default: `150`)
- `DEFAULT_REPLACE_VERSIONS`: whether to replace the versions  (default: `True`)
- `MU_NETWORK`: the network in which the created consumers should reside
