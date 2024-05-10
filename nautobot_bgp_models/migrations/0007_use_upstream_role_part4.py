# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name

from django.db import migrations
import django.db.models.deletion
import nautobot.extras.models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_bgp_models", "0006_use_upstream_role_part3"),
    ]

    operations = [
        migrations.AlterField(
            model_name="peerendpoint",
            name="role",
            field=nautobot.extras.models.roles.RoleField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bgp_peer_endpoints",
                to="extras.role",
            ),
        ),
        migrations.AlterField(
            model_name="peergroup",
            name="role",
            field=nautobot.extras.models.roles.RoleField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bgp_peer_groups",
                to="extras.role",
            ),
        ),
        migrations.AlterField(
            model_name="peergrouptemplate",
            name="role",
            field=nautobot.extras.models.roles.RoleField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bgp_peer_group_templates",
                to="extras.role",
            ),
        ),
    ]
