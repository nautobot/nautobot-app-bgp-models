# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_bgp_models", "0008_nautobotv2_updates"),
    ]

    operations = [
        migrations.AddField(
            model_name="peerendpoint",
            name="label",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
