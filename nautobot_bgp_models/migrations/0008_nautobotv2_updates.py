# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name

import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.extras.models.roles
import nautobot.extras.models.statuses
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_bgp_models", "0007_use_upstream_role_part4"),
    ]

    operations = [
        migrations.AlterField(
            model_name="addressfamily",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="autonomoussystem",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="autonomoussystem",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="autonomous_systems",
                to="extras.status",
            ),
        ),
        migrations.AlterField(
            model_name="autonomoussystem",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="bgproutinginstance",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="bgproutinginstance",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bgp_routing_instances",
                to="extras.status",
            ),
        ),
        migrations.AlterField(
            model_name="bgproutinginstance",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="peerendpoint",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="peerendpoint",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="peergroup",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="peergroup",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="peergrouptemplate",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="peergrouptemplate",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="peering",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="peering",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bgp_peerings",
                to="extras.status",
            ),
        ),
        migrations.AlterModelOptions(
            name="peerendpoint",
            options={"verbose_name": "BGP Peer Endpoint"},
        ),
        migrations.AlterModelOptions(
            name="peergroup",
            options={"ordering": ["name"], "verbose_name": "BGP Peer Group"},
        ),
        migrations.AlterField(
            model_name="peerendpointaddressfamily",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="peergroupaddressfamily",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
