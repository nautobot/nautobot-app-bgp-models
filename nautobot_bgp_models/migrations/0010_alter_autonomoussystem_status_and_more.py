# Generated by Django 4.2.14 on 2024-08-07 16:00

import django.db.models.deletion
import nautobot.extras.models.roles
import nautobot.extras.models.statuses
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_bgp_models", "0009_autonomoussystemrange"),
    ]

    operations = [
        migrations.AlterField(
            model_name="autonomoussystem",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="extras.status"
            ),
        ),
        migrations.AlterField(
            model_name="bgproutinginstance",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="extras.status"
            ),
        ),
        migrations.AlterField(
            model_name="peerendpoint",
            name="role",
            field=nautobot.extras.models.roles.RoleField(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="extras.role"
            ),
        ),
        migrations.AlterField(
            model_name="peergroup",
            name="role",
            field=nautobot.extras.models.roles.RoleField(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="extras.role"
            ),
        ),
        migrations.AlterField(
            model_name="peergrouptemplate",
            name="role",
            field=nautobot.extras.models.roles.RoleField(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="extras.role"
            ),
        ),
        migrations.AlterField(
            model_name="peering",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="extras.status"
            ),
        ),
    ]
