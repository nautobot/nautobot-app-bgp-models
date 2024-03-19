"""App declaration for nautobot_bgp_models."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from django.db.models.signals import post_migrate
from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class NautobotBGPModelsConfig(NautobotAppConfig):
    """App configuration for the nautobot_bgp_models app."""

    name = "nautobot_bgp_models"
    verbose_name = "BGP Models"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot BGP Models App."
    base_url = "bgp"
    required_settings = []
    min_version = "2.0.3"
    max_version = "2.9999"
    default_settings = {
        "default_statuses": {
            "AutonomousSystem": ["Active", "Available", "Planned"],
            "BGPRoutingInstance": ["Planned", "Active", "Decommissioned"],
            "Peering": ["Active", "Decommissioned", "Deprovisioning", "Offline", "Planned", "Provisioning"],
        }
    }
    caching_config = {}

    def ready(self):
        """Callback invoked after the app is loaded."""
        super().ready()

        # Attempt to register versioned models & tables with Dolt if it is
        # available.
        from . import dolt_compat  # noqa pylint: disable=import-outside-toplevel, unused-import

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_statuses,
        )

        post_migrate.connect(post_migrate_create_statuses, sender=self)


config = NautobotBGPModelsConfig  # pylint:disable=invalid-name
