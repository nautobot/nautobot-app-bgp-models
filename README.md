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

> The plugin is compatible with Nautobot 1.5.4 and higher

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

![Peering List](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peering_list.png)

![Peering](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peering_01.png)

![Peer Endpoint](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peer_endpoint_01.png)

![Peer Group](https://github.com/nautobot/nautobot-plugin-bgp-models/blob/main/docs/images/peer_group_01.png)

## Contributing

Pull requests are welcomed and automatically built and tested against multiple version of Python and multiple version of Nautobot through TravisCI.

The project is packaged with a light development environment based on `docker-compose` to help with the local development of the project and to run the tests within TravisCI.

The project is following Network to Code software development guideline and is leveraging:

- Black, Pylint, Bandit and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

## Questions

For any questions or comments, please check the [FAQ](FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #networktocode).
Sign up [here](http://slack.networktocode.com/)
