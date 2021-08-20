# Nautobot BGP Models Plugin

A plugin for [Nautobot](https://github.com/nautobot/nautobot) to extend the core models with BGP specific models.

> Initial development of this plugin was sponsored by Riot Games, Inc.
 
## Data Models

This plugin adds the following new data models into Nautobot:
- AutonomousSystem
- PeerSession
- PeerEndpoint
- PeerGroup
- PeeringRole
- AddressFamily
The BGP plugin also makes use of a number of custom fields added to the Device model, and defines several custom relationships between data models. 

A key motivation behind this design is the idea that the Source of Truth should take a network-wide view of the BGP configuration, rather than a device-per-device view. This most directly applies to the data models for autonomous systems (ASNs) and BGP peering sessions.

All the data models introduced by the BGP plugin support the following Nautobot features:
- Rest API
- GraphQL
- Custom fields
- Custom Links
- Relationships
- Change logging
- Custom data validation logic
- Webhooks

> The data model defined by this plugin takes inspiration from the IETF BGP data model (https://tools.ietf.org/html/draft-ietf-idr-bgp-model-10), and the [Peering Manager](https://github.com/peering-manager/peering-manager) open-source application.

### AutonomousSystem
This model represents a network-wide description of a BGP autonomous system (AS). It has fields including the actual AS number (ASN), a description field, and a FK to a Nautobot Status object.

### PeerSession
This model represents the shared configuration of a single BGP peer relationship between two devices. It has FKs to two BGPPeerEndpoint records, and additional fields including:
- Status (FK to Nautobot Status)
- Role (FK to PeeringRole)
- Authentication Key (optional, string, encrypted at rest)

> The nature of a session as BGP “internal” or “external” is useful in the construction of queries and filters, but does not need to be stored as an actual database attribute (as it is implied by whether the ASNs of the two BGPPeerEndpoints involved are identical or different). It is implemented as a derived property of the `PeerSession` model.

### PeerEndpoint
This model represents the configuration of a single device with respect to a single BGP peering session. It does not store configuration that must match symmetrically between peer devices (such as a common authentication key), which would instead be stored on a `PeerSession` record (see below). 

Note that in the case of an external peering (device in the locally managed network peering to a remote endpoint belonging to an AS not managed within this network), while there generally will not be a Device record representing the remote endpoint, there will need to be a `PeerEndpoint` record representing it, at a minimum storing the IP address and ASN of the remote endpoint.
It has an optional FK to a Nautobot Device record, an optional foreign-key relationship to a PeerGroup (as a peer session may or may not belong to a peer-group), and additional keys including
- Local IP (FK to Nautobot IPAddress)
- VRF (optional, FK to a Nautobot VRF)
- Update-Source Interface (optional, FK to Nautobot Interface)
- Router-ID (optional, FK to Nautobot IPAddress)
- ASN (optional, FK to AutonomousSystem)
- Description (string)
- Enabled (bool)
- Import Policy (optional, string)
- Export Policy (optional, string)
- Maximum Prefixes (optional, integer)
- Send-Community (optional, boolean)
- Enforce First ASN (optional, boolean)

### AddressFamily
This model represents configuration of a BGP address-family (AFI-SAFI). As AFI-SAFI configuration may be applied at various levels (global, peer-group, peer-session), this model attempts to represent any of those. It has a FK to a Nautobot device record, a locally unique AFI (address-family identifier) field, optional foreign-key relationships to `PeerGroup` or `PeerSession` (mutually exclusive, either or both may be null but both may not be non-null simultaneously) and additional fields including:
- Import Policy (optional, string)
- Export Policy (optional, string)
- Static Redistribution Policy (optional, string)
## PeerGroup
This model represents common/template configuration for a group of functionally related BGP peers. It has a foreign-key (FK) to a Device, a locally unique Name field, and additional fields including:
- Role (FK to PeeringRole)
- VRF (optional, FK to a Nautobot VRF)
- Update-Source Interface (optional, FK to Nautobot Interface)
- Router-ID (optional, FK to Nautobot IPAddress)
- ASN (optional, FK to AutonomousSystem)
- Description (string)
- Enabled (bool)
- Maximum-paths (iBGP, eBGP, eiBGP) - optional integers
- Multipath (optional, bool)
- BFD multiplier (optional, integer)
- BFD minimum interval (optional, integer)
- BFD fast-detection (optional, bool)

### PeeringRole
This model operates similarly to Nautobot’s Status and Tag models, in that instances of this model describe various valid values for the type field on `PeerGroup` and/or `PeerSession`. Similar to those models, this model has fields including a unique name, unique slug, and a HTML color value.


## Installation

The plugin is available as a Python package in PyPI and can be installed with `pip`:

```shell
pip install nautobot-bgp-models
```

> The plugin is compatible with Nautobot 1.0.2 and higher

To ensure Nautobot BGP Models Plugin is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-bgp-models` package:

```no-highlight
# echo nautobot-bgp-models >> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your `nautobot_config.py`

```python
# In your configuration.py
PLUGINS = ["nautobot_bgp_models"]
```


## Contributing

Pull requests are welcomed and automatically built and tested against multiple version of Python and multiple version of Nautobot through TravisCI.

The project is packaged with a light development environment based on `docker-compose` to help with the local development of the project and to run the tests within TravisCI.

The project is following Network to Code software development guideline and is leveraging:

- Black, Pylint, Bandit and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

### Development Environment

The development environment can be used in 2 ways. First, with a local poetry environment if you wish to develop outside of Docker. Second, inside of a docker container.

#### Invoke tasks

The [PyInvoke](http://www.pyinvoke.org/) library is used to provide some helper commands based on the environment.  There are a few configuration parameters which can be passed to PyInvoke to override the default configuration:

* `nautobot_ver`: the version of Nautobot to use as a base for any built docker containers (default: develop-latest)
* `project_name`: the default docker compose project name (default: nautobot-bgp-models)
* `python_ver`: the version of Python to use as a base for any built docker containers (default: 3.6)
* `local`: a boolean flag indicating if invoke tasks should be run on the host or inside the docker containers (default: False, commands will be run in docker containers)
* `compose_dir`: the full path to a directory containing the project compose files
* `compose_files`: a list of compose files applied in order (see [Multiple Compose files](https://docs.docker.com/compose/extends/#multiple-compose-files) for more information)

Using PyInvoke these configuration options can be overridden using [several methods](http://docs.pyinvoke.org/en/stable/concepts/configuration.html).  Perhaps the simplest is simply setting an environment variable `INVOKE_NAUTOBOT_BGP_MODELS_VARIABLE_NAME` where `VARIABLE_NAME` is the variable you are trying to override.  The only exception is `compose_files`, because it is a list it must be overridden in a yaml file.  There is an example `invoke.yml` in this directory which can be used as a starting point.

#### Local Poetry Development Environment

1.  Copy `development/creds.example.env` to `development/creds.env` (This file will be ignored by git and docker)
2.  Uncomment the `POSTGRES_HOST`, `REDIS_HOST`, and `NAUTOBOT_ROOT` variables in `development/creds.env`
3.  Create an invoke.yml with the following contents at the root of the repo:

```shell
---
nautobot_bgp_models:
  local: true
  compose_files:
    - "docker-compose.requirements.yml"
    - "docker-compose.local.yml"
```

3.  Run the following commands:

```shell
poetry shell
poetry install
export $(cat development/dev.env | xargs)
export $(cat development/creds.env | xargs) 
```

4.  You can now run nautobot-server commands as you would from the [Nautobot documentation](https://nautobot.readthedocs.io/en/latest/) for example to start the development server:

```shell
nautobot-server runserver 0.0.0.0:8080 --insecure
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).

#### Docker Development Environment

This project is managed by [Python Poetry](https://python-poetry.org/) and has a few requirements to setup your development environment:

1.  Install Poetry, see the [Poetry Documentation](https://python-poetry.org/docs/#installation) for your operating system.
2.  Install Docker, see the [Docker documentation](https://docs.docker.com/get-docker/) for your operating system.

Once you have Poetry and Docker installed you can run the following commands to install all other development dependencies in an isolated python virtual environment:

```shell
poetry shell
poetry install
invoke start
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).

### CLI Helper Commands

The project is coming with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories `dev environment`, `utility` and `testing`. 

Each command can be executed with `invoke <command>`. Environment variables `INVOKE_NAUTOBOT_BGP_MODELS_PYTHON_VER` and `INVOKE_NAUTOBOT_BGP_MODELS_NAUTOBOT_VER` may be specified to override the default versions. Each command also has its own help `invoke <command> --help`

#### Docker dev environment

```no-highlight
  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  restart          Restart Nautobot and its dependencies.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
```

#### Utility

```no-highlight
  cli              Launch a bash shell inside the running Nautobot container.
  create-user      Create a new user in django (default: admin), will prompt for password.
  makemigrations   Run Make Migration in Django.
  nbshell          Launch a nbshell session.
```

#### Testing

```no-highlight
  bandit           Run bandit to validate basic static code security analysis.
  black            Run black to check that Python files adhere to its style standards.
  flake8           This will run flake8 for the specified name and Python version.
  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.
  pylint           Run pylint code analysis.
  tests            Run all tests for this plugin.
  unittest         Run Django unit tests for the plugin.
```

## Questions

For any questions or comments, please check the [FAQ](FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #networktocode).
Sign up [here](http://slack.networktocode.com/)
