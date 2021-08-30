"""Nautobot signal handler functions for nautobot_bgp_models."""

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.choices import RelationshipTypeChoices


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
    ]:
        Relationship.objects.get_or_create(name=relationship_dict["name"], defaults=relationship_dict)


@receiver(pre_delete, sender="dcim.Device")
def delete_device_objects(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Delete all PeerGroups and AddressFamilies associated with this Device."""
    from django.contrib.contenttypes.models import ContentType  # pylint: disable=import-outside-toplevel
    from .models import PeerGroup, AddressFamily  # pylint: disable=import-outside-toplevel

    content_type = ContentType.objects.get_for_model(instance)
    PeerGroup.objects.filter(device_content_type=content_type, device_object_id=instance.pk).delete()
    AddressFamily.objects.filter(device_content_type=content_type, device_object_id=instance.pk).delete()
