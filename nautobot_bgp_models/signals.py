"""Nautobot signal handler functions for nautobot_bgp_models."""

from django.apps import apps as global_apps
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from nautobot_bgp_models.models import PeerGroup


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
        for slug in default_statuses:
            try:
                status = Status.objects.get(slug=slug)
            except Status.DoesNotExist:
                print(f"nautobot_bgp_models: Unable to find status: {slug} .. SKIPPING")
                continue

            if ct_model not in status.content_types.all():
                status.content_types.add(ct_model)
                status.save()


@receiver(post_save, sender=PeerGroup)
def handle_peergroup_updates(instance, created, raw=False, **kwargs):
    """
    Update child PeerEndpoints if PeerGroup has changed.
    This function should especially update all endpoint's IPs to support change
    of the `peer_group.source_ip` or `peer_group.source_interface`. Change of these attributes impacts
    effective Peer Endpoints IP addresses as PeerEndpoint might inherit values from the PeerGroup
    """
    if raw or created:
        return
    with transaction.atomic():
        for endpoint in instance.endpoints.all():
            if endpoint.local_ip != endpoint.ip:
                endpoint.ip = endpoint.local_ip
                endpoint.save()
