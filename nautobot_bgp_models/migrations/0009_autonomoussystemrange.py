# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name

import uuid
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.dcim.fields
import nautobot.extras.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ("tenancy", "0008_tagsfield"),
        ("extras", "0098_rename_data_jobresult_result"),
        ("nautobot_bgp_models", "0008_nautobotv2_updates"),
    ]

    operations = [
        migrations.CreateModel(
            name="AutonomousSystemRange",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("asn_min", nautobot.dcim.fields.ASNField()),
                ("asn_max", nautobot.dcim.fields.ASNField()),
                ("description", models.CharField(blank=True, max_length=255)),
                ("tags", nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="tenancy.tenant"
                    ),
                ),
            ],
            options={
                "verbose_name": "Autonomous System Range",
                "ordering": ["asn_min"],
            },
            bases=(
                models.Model,
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
            ),
        ),
    ]
