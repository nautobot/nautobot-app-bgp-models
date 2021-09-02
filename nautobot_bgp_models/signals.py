"""Nautobot signal handler functions for nautobot_bgp_models."""

from nautobot_bgp_models.models import AddressFamily
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.choices import RelationshipTypeChoices

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_bgp_models"]


def post_migrate_create_custom_fields(apps, **kwargs):
    """Callback function for post_migrate() -- create CustomField records."""
    # pylint: disable=invalid-name
    ContentType = apps.get_model("contenttypes", "ContentType")
    Device = apps.get_model("dcim", "Device")
    CustomField = apps.get_model("extras", "CustomField")

    for device_cf_dict in [
        {
            "name": "bgp_ecmp_maximum_paths",
            "type": CustomFieldTypeChoices.TYPE_INTEGER,
            "label": "BGP ECMP Maximum Paths",
            # TODO validation_minimum, validation_maximum, default
        },
    ]:
        field, _ = CustomField.objects.get_or_create(name=device_cf_dict["name"], defaults=device_cf_dict)
        field.content_types.set([ContentType.objects.get_for_model(Device)])


def post_migrate_create_relationships(sender, apps, **kwargs):
    """Callback function for post_migrate() -- create Relationship records."""
    # pylint: disable=invalid-name
    AutonomousSystem = sender.get_model("AutonomousSystem")
    PeerGroup = sender.get_model("PeerGroup")
    AddressFamily = sender.get_model("AddressFamily")
    ContentType = apps.get_model("contenttypes", "ContentType")
    Device = apps.get_model("dcim", "Device")
    IPAddress = apps.get_model("ipam", "IPAddress")
    Relationship = apps.get_model("extras", "Relationship")

    for relationship_dict in [
        {
            "name": "BGP Autonomous System",
            "slug": "bgp_asn",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
            "source_type": ContentType.objects.get_for_model(AutonomousSystem),
            "source_label": "Autonomous System Members",
            "destination_type": ContentType.objects.get_for_model(Device),
            "destination_label": "BGP Autonomous System",
        },
        {
            "name": "BGP Router ID",
            "slug": "bgp_device_router_id",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_ONE,
            "source_type": ContentType.objects.get_for_model(Device),
            "source_label": "BGP Router ID",
            # TODO source_filter
            "destination_type": ContentType.objects.get_for_model(IPAddress),
            "destination_label": "BGP Router-ID for Device",
            "destination_filter": {"role": "loopback"},
        },
        {
            "name": "BGP Device <> Peer Group",
            "slug": "bgp_device_peergroup",
            "type": RelationshipTypeChoices.TYPE_MANY_TO_MANY,
            "source_type": ContentType.objects.get_for_model(Device),
            "source_label": "BGP Peer Groups",
            "destination_type": ContentType.objects.get_for_model(PeerGroup),
        },
        {
            "name": "BGP Device <> AddressFamily",
            "slug": "bgp_device_af",
            "type": RelationshipTypeChoices.TYPE_MANY_TO_MANY,
            "source_type": ContentType.objects.get_for_model(Device),
            "source_label": "BGP Address Families",
            "destination_type": ContentType.objects.get_for_model(AddressFamily),
        },
    ]:
        Relationship.objects.get_or_create(name=relationship_dict["name"], defaults=relationship_dict)


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


@receiver(pre_delete, sender="dcim.Device")
def delete_device_objects(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Delete all PeerGroups and AddressFamilies associated with this Device."""
    from django.contrib.contenttypes.models import ContentType  # pylint: disable=import-outside-toplevel
    from .models import PeerGroup, AddressFamily  # pylint: disable=import-outside-toplevel

    content_type = ContentType.objects.get_for_model(instance)
    PeerGroup.objects.filter(device_content_type=content_type, device_object_id=instance.pk).delete()
    AddressFamily.objects.filter(device_content_type=content_type, device_object_id=instance.pk).delete()
