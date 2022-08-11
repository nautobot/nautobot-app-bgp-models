# Nautobot BGP Models Plugin

A plugin for [Nautobot](https://github.com/nautobot/nautobot) extending the core models with BGP-specific models.

New models enable modeling and management of BGP peerings, whether or not the peer device is present in Nautobot.

> The initial development of this plugin was sponsored by Riot Games, Inc. 

## Data Models

Navigate to [Data Models](docs/cisco_use_case.md) for detailed descriptions on additional data models provided in the plugin.

## Use Cases

To make the start with the plugin easier, we provide two example use cases for common OS platforms: Cisco and Juniper.

### Cisco Configuration Modeling and Rendering

Navigate to [Cisco Example Use Case](docs/cisco_use_case.md) for detailed instructions how to consume BGP Models plugin on Cisco devices.

### Juniper Configuration Modeling and Rendering

Navigate to [Juniper Example Use Case](docs/juniper_use_case.md) for detailed instructions how to consume BGP Models plugin on Juniper devices.

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
            "Peering": ["active", "decommissioned", "deprovisioning", "offline", "planned", "provisioning"],
        }
    }
}
```

In the `default_statuses` section, you can define a list of default statuses to make available to `AutonomousSystem` and/or `Peering`. The lists must be composed of valid slugs of existing Status objects.

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
