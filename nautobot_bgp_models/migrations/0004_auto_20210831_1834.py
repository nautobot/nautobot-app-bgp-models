# Generated by Django 3.1.8 on 2021-08-31 18:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("nautobot_bgp_models", "0003_addressfamily_ordering"),
    ]

    operations = [
        migrations.AlterField(
            model_name="peerendpoint",
            name="session",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="endpoints",
                to="nautobot_bgp_models.peersession",
            ),
        ),
    ]