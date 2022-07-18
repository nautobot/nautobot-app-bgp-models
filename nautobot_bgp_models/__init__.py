"""Plugin declaration for nautobot_bgp_models."""

try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from django.db.models.signals import post_migrate

from nautobot.extras.plugins import PluginConfig


class NautobotBGPModelsConfig(PluginConfig):
    """Plugin configuration for the nautobot_bgp_models plugin."""

    name = "nautobot_bgp_models"
    verbose_name = "BGP Models"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot BGP Models Plugin."
    base_url = "bgp"
    required_settings = []
    min_version = "1.3.0"
    max_version = "1.999"
    default_settings = {
        "default_statuses": {
            "AutonomousSystem": ["active", "available", "planned"],
            "Peering": ["active", "decommissioned", "deprovisioning", "offline", "planned", "provisioning"],
        }
    }
    caching_config = {}

    def ready(self):
        """Callback invoked after the plugin is loaded."""
        super().ready()

        # Attempt to register versioned models & tables with Dolt if it is
        # available.
        from . import dolt_compat  # noqa pylint: disable=import-outside-toplevel, unused-import

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_statuses,
        )

        post_migrate.connect(post_migrate_create_statuses, sender=self)


config = NautobotBGPModelsConfig  # pylint:disable=invalid-name
