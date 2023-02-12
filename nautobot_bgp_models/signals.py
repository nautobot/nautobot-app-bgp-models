"""Nautobot signal handler functions for nautobot_bgp_models."""

from django.apps import apps as global_apps
from django.conf import settings

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_bgp_models"]


def post_migrate_create_statuses(sender, *, apps=global_apps, **kwargs):
    """Callback function for post_migrate() -- create default Statuses."""
    # pylint: disable=invalid-name
    if not apps:
        return

    Status = apps.get_model("extras", "Status")

    for model_name, default_statuses in PLUGIN_SETTINGS.get("default_statuses", {}).items():
        model = sender.get_model(model_name)

        ContentType = apps.get_model("contenttypes", "ContentType")
        ct_model = ContentType.objects.get_for_model(model)
        for name in default_statuses:
            try:
                status = Status.objects.get(name=name)
            except Status.DoesNotExist:
                print(f"nautobot_bgp_models: Unable to find status: {name} .. SKIPPING")
                continue

            if ct_model not in status.content_types.all():
                status.content_types.add(ct_model)
                status.save()
