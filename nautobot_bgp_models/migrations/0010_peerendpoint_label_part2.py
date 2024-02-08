# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name

from django.db import migrations


def create_labels_for_existing_endpoints(apps, schema_editor):  # pylint: disable=unused-argument
    PeerEndpoint = apps.get_model("nautobot_bgp_models", "PeerEndpoint")

    for index, peer_endpoint in enumerate(PeerEndpoint.objects.order_by("created"), start=1):
        peer_endpoint.label = index
        peer_endpoint.save()


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_bgp_models", "0009_peerendpoint_label_part1"),
    ]

    operations = [
        migrations.RunPython(create_labels_for_existing_endpoints, migrations.RunPython.noop),
    ]
