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
    min_version = "1.0.2"
    max_version = "1.999"
    default_settings = {}
    caching_config = {}

    def ready(self):
        """Callback invoked after the plugin is loaded."""
        super().ready()

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_custom_fields,
            post_migrate_create_relationships,
        )

        post_migrate.connect(post_migrate_create_custom_fields, sender=self)
        post_migrate.connect(post_migrate_create_relationships, sender=self)


config = NautobotBGPModelsConfig  # pylint:disable=invalid-name
