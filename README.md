# Nautobot BGP Models Plugin

A plugin for [Nautobot](https://github.com/nautobot/nautobot) to extend the core models with BGP specific models. 
All types of BGP peerings can be model and managed, whether or not the device is present in Nautobot.

> The initial development of this plugin was sponsored by Riot Games, Inc.

## Data Models

This plugin adds the following new data models into Nautobot:
- Autonomous System
- Routing Instance
- Peer Endpoint
- Peer Group
- Peer Group Template
- Address Family
- Peering
- Peering Role

A key motivation behind this design is the idea that the Source of Truth should take a network-wide view of the BGP configuration, rather than a device-per-device view. This most directly applies to the data models for autonomous systems (ASNs), BGP peerings and network-wide templates (Peer Groups).

All the data models introduced by the BGP plugin support the following Nautobot features:
- Rest API
- GraphQL
- Custom fields
- Custom Links
- Relationships
- Change logging
- Custom data validation logic
- Webhooks

> The data model defined by this plugin takes inspirations from the Openconfig BGP data model (https://yangcatalog.org/api/services/tree/openconfig-bgp@2021-06-16.yang) and the RFC 9234 (https://datatracker.ietf.org/doc/rfc9234/)

### AutonomousSystem
This model represents a network-wide description of a BGP autonomous system (AS). It has fields including the actual AS number (ASN), a description field, foreign key (FK) to a Nautobot `Provider` object, and a FK to a Nautobot `Status` object.

### BGPRoutingInstance
This model represents a device specific BGP process. It has a mandatory FK to a Nautobot `Device`, mandatory FK to a `AutonomousSystem` and following fields: 

- Router ID (optional, FK to Nautobot `IPAddress`,
- Description (optional, string)
- Extra Attributes (optional, JSON)

### PeerEndpoint
This model represents the configuration of a single device with respect to a single BGP peering. It does not store configuration that must match symmetrically between peer devices (such as a common authentication key). 

Note that in the case of an external peering (device in the locally managed network peering to a remote endpoint belonging to an AS not managed within this network), while there generally will not be a Device record representing the remote endpoint, there will need to be a `PeerEndpoint` record representing it, at a minimum storing the IP address and ASN of the remote endpoint.

`PeerEndpoint` model has a mandatory FK to a BGP Routing Instance (`BGPRoutingInstance`) record, an optional foreign-key relationship to a `PeerGroup`, and additional keys including:

- ASN (optional, FK to `AutonomousSystem`)
- Peer (optional, FK to `PeerEndpoint`)
- Source IP (optional, FK to Nautobot `IPAddress`, mutually-exclusive with Source Interface)
- Source Interface (optional, FK to Nautobot `Interface`, mutually-exclusive with Source IP)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Import Policy (optional, string)
- Export Policy (optional, string)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

#### PeerEndpoint Local-IP
To ease the data presentation and consumption, `PeerEndpoint` provides also a property named `local_ip`.
The value of this property will be presented in plugin's Grapical User Interface (GUI), and can be used to render configuration templates.

As Source-IP and Source-Interface could be defined at multiple inheritance levels, each Peer Endpoint will have a `local_ip` determined based on the following order:
1. `PeerEndpoint`'s `source_ip` attribute (if exists)
2. `Peer Group`'s `source_ip` attribute (if exists)
3. `PeerEndpoint`'s `source_interface` attribute (if exists)
4. `PeerGroup`'s `source_interface` attribute (if exists)

### PeerGroup
This model represents common configuration for a group of functionally related BGP peers. `PeerGroup` aims to represent device-specific configuration, and it has a mandatory `Name` field, optional FK to a network-wide `PeerGroupTemplate`, and additional fields including:

- ASN (optional, FK to `AutonomousSystem`)
- Source IP (optional, FK to Nautobot `IPAddress`, mutually-exclusive with Source Interface)
- Source Interface (optional, FK to Nautobot `Interface`, mutually-exclusive with Source IP)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Import Policy (optional, string)
- Export Policy (optional, string)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

### PeerGroupTemplate
This model represents network-wide configuration for `PeerGroups`. `PeerGroupTemplate` aims to represent a global configuration, and it has a mandatory `Name` field, and following fields:

- ASN (optional, FK to `AutonomousSystem`)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Import Policy (optional, string)
- Export Policy (optional, string)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

### Extra Attributes
Additional BGP object's attributes can be modelled by "Extra Attributes". Extra_attributes is a JSON type fields allowing to store data modelled by user.
Extra attributes follow the inheritance pattern, thus allowing for merging the inherited extra attributes.

Examples of the extra attributes might include:
```json
{"ttl-security": 1, "timers": [6, 20] }
```

Extra Attributes are available for following models:
- `PeerEndpoint`
- `PeerGroup`
- `PeerGroupTemplate`
- `BGPRoutingInstance`

### AddressFamily
This model represents configuration of a BGP address-family (AFI-SAFI). AddressFamily aims to represent a device specific Address Family instance.
It has a locally unique AFI (address-family identifier) field, optional VRF field (FK to Nautobot `VRF`) and following fields:
- Import Policy (optional, string)
- Export Policy (optional, string)

(*) The network-wide modelling of AddressFamilies will be implemented in the future with `AddressFamilyTemplate` model similar to the `PeerGroupTemplate`.
The device-specific `PeerEndpoint` custom modeling will be implemented in the future with `PeerEndpointContext` and `PeerGroupContext` models.

### Peering
This model represents the shared configuration of a single BGP peer relationship between two endpoints. It has FKs to two `PeerEndpoint` records (representing the two devices involved in the peering), and additional fields including:
- Status (FK to Nautobot `Status`)

> The nature of a session as BGP “internal” or “external” is useful in the construction of queries and filters, but does not need to be stored as an actual database attribute (as it is implied by whether the ASNs of the two BGPPeerEndpoints involved are identical or different). It is implemented as a derived property of the `Peering` model.

### PeeringRole
This model operates similarly to Nautobot’s `Status` and `Tag` models, in that instances of this model describe various valid values for the type field on `PeerGroup` and/or `PeerSession`. Similar to those models, this model has fields including a unique name, unique slug, and a HTML color value.

### Inheritance between models

Some models have a built-in inheritance similar to what BGP supports with PeerGroup. The inheritance can take multi-level lookup between BGP objects, in this case the first found object with the assigned attribute will be considered as an inheritance source.

Example **PeerEndpoint** inheritance details:
- A `PeerEndpoint` inherits `AutonomousSystem` and `extra_attributes` fields from:
  - `PeerGroup`
  - `PeerGroupTemplate`
  - `BGPRoutingInstance`


- A `PeerEndpoint` inherits `description`, `enabled`, `export_policy`, `import_policy` fields from:
  - `PeerGroup`
  - `PeerGroupTemplate`


- A `PeerEndpoint` inherits `source_ip`, `source_interface` fields from:
  - `PeerGroup`

As an example, a `PeerEndpoint` associated with a `PeerGroup` will automatically inherit above attributes of the `PeerGroup` that haven't been defined at the `PeerEndpoint` level. If an attribute is defined on both, the value defined on the `PeerEndpoint` will be used.

The inherited values will be automatically displayed in the UI and can be retrieve from the REST API with the additional `?include_inherited=true` parameter.

(*) **BGP models Custom Fields and GraphQL currently does not offer support for BGP Field Inheritance.** GraphQL issue is tracked under https://github.com/nautobot/nautobot-plugin-bgp-models/issues/43 

Following is the complete documentation of the field inheritance pattern. Models are listed from top priority to the least priority, the first model with an assigned attribute value will be used as an inheritance source.

**PeerEndpoint**:

| **Attribute** | **Inheritance from model**                             |
|---|--------------------------------------------------------|
| autonomous_system | PeerGroup &rarr; PeerGroupTemplate &rarr; BGPRoutingInstance |
| extra_attributes | PeerGroup &rarr; PeerGroupTemplate &rarr; BGPRoutingInstance |
| description | PeerGroup &rarr; PeerGroupTemplate |
| enabled | PeerGroup &rarr; PeerGroupTemplate |
| export_policy | PeerGroup &rarr; PeerGroupTemplate |
| import_policy | PeerGroup &rarr; PeerGroupTemplate |
| role | PeerGroup &rarr; PeerGroupTemplate |
| source_ip | PeerGroup |
| source_interface | PeerGroup |

**PeerGroup**:

| **Attribute** | **Inheritance from model** |
|------|-------------------|
| extra_attributes | PeerGroupTemplate &rarr; BGPRoutingInstance |
| autonomous_system | PeerGroupTemplate |
| description | PeerGroupTemplate |
| enabled | PeerGroupTemplate |
| export_policy | PeerGroupTemplate |
| import_policy | PeerGroupTemplate |
| role | PeerGroupTemplate |

## Installation

The plugin is available as a Python package in PyPI and can be installed with `pip`:

```shell
pip install nautobot-bgp-models
```

> The plugin is compatible with Nautobot 1.3 and higher

To ensure Nautobot BGP Models Plugin is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-bgp-models` package:

```no-highlight
# echo nautobot-bgp-models >> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your `nautobot_config.py`

```python
# In your configuration.py
PLUGINS = ["nautobot_bgp_models"]
```
```python
PLUGINS_CONFIG = {
    "nautobot_bgp_models": {
        "default_statuses": {
            "AutonomousSystem": ["active", "available", "planned"],
            "PeerSession": ["active", "decommissioned", "deprovisioning", "offline", "planned", "provisioning"],
        }
    }
}
```
In the `default_statuses` section, you can define a list of default statuses to make available to `AutonomousSystem` and/or `PeerSession`. The lists must be composed of valid slugs of existing Status objects.

## Screenshots

![Menu](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/main-page-menu.png)

![Autonomous System](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/autonomous_system_01.png)

![Peering List](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peer_session_list.png)

![Peering](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peering_01.png)

![Peer Endpoint](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peer_endpoint_01.png)

![Peer Group](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peer_group_01.png)

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
