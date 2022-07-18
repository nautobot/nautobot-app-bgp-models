"""Nautobot signal handler functions for nautobot_bgp_models."""

from django.conf import settings

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_bgp_models"]


def post_migrate_create_statuses(sender, apps, **kwargs):
    """Callback function for post_migrate() -- create default Statuses."""
    # pylint: disable=invalid-name
    Status = apps.get_model("extras", "Status")

    for model_name, default_statuses in PLUGIN_SETTINGS.get("default_statuses", {}).items():
        model = sender.get_model(model_name)

        ContentType = apps.get_model("contenttypes", "ContentType")
        ct_model = ContentType.objects.get_for_model(model)
        for slug in default_statuses:
            try:
                status = Status.objects.get(slug=slug)
            except Status.DoesNotExist:
                print(f"nautobot_bgp_models: Unable to find status: {slug} .. SKIPPING")
                continue

            if ct_model not in status.content_types.all():
                status.content_types.add(ct_model)
                status.save()
