# ldes-consumer-manager
This service provides an interface to manage [ldes-consumer-service](https://github.com/redpencilio/ldes-consumer-service) containers. It has irect access to the docker daemon, so do not expose it to the world.

## Usage

Add to docker-compose:
```
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
