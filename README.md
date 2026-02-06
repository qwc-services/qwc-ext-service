[![](https://github.com/qwc-services/qwc-ext-service/workflows/build/badge.svg)](https://github.com/qwc-services/qwc-ext-service/actions)
[![docker](https://img.shields.io/docker/v/sourcepole/qwc-ext-service?label=Docker%20image&sort=semver)](https://hub.docker.com/r/sourcepole/qwc-ext-service)

QWC external link service
=========================

Proxy service for external application links, identified by a program name, with access control.

Setup
-----

Declare the resource type in the config database:

    INSERT INTO qwc_config.resource_types(name, description, list_order) values ('external_links', 'External link name', <list_order>);

Pick `<list_order>` according to the desired ordering position in the resource selection menu in the QWC Admin GUI.

Configuration
-------------

The static config files are stored as JSON files in `$CONFIG_PATH` with subdirectories for each tenant,
e.g. `$CONFIG_PATH/default/*.json`. The default tenant name is `default`.

### JSON config

* [JSON schema](schemas/qwc-ext-service.json)
* File location: `$CONFIG_PATH/<tenant>/extConfig.json`

Example:
```json
{
  "$schema": "https://raw.githubusercontent.com/qwc-services/qwc-ext-service/master/schemas/qwc-ext-service.json",
  "service": "ext",
  "resources": {
    "external_links": [
      {"name": "prog1", "url": "http://my.secret.site/path/?tenant=$tenant$&user=$username$"}
    ]
  }
}
```

Run locally
-----------

Install dependencies and run:

    # Setup venv
    uv venv .venv

    export CONFIG_PATH=<CONFIG_PATH>
    uv run src/server.py

To use configs from a `qwc-docker` setup, set `CONFIG_PATH=<...>/qwc-docker/volumes/config`.

Set `FLASK_DEBUG=1` for additional debug output.

Set `FLASK_RUN_PORT=<port>` to change the default port (default: `5000`).

API documentation:

    http://localhost:$FLASK_RUN_PORT/api/

Docker usage
------------

The Docker image is published on [Dockerhub](https://hub.docker.com/r/sourcepole/qwc-ext-service).

See sample [docker-compose.yml](https://github.com/qwc-services/qwc-docker/blob/master/docker-compose-example.yml) of [qwc-docker](https://github.com/qwc-services/qwc-docker).
