# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name
# Generated by Django 3.2.17 on 2023-02-12 20:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_bgp_models", "0005_use_upstream_role_part2"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="peerendpoint",
            name="role",
        ),
        migrations.RemoveField(
            model_name="peergroup",
            name="role",
        ),
        migrations.RemoveField(
            model_name="peergrouptemplate",
            name="role",
        ),
        migrations.DeleteModel(
            name="PeeringRole",
        ),
        migrations.RenameField(
            model_name="peergroup",
            old_name="role_new",
            new_name="role",
        ),
        migrations.RenameField(
            model_name="peergrouptemplate",
            old_name="role_new",
            new_name="role",
        ),
        migrations.RenameField(
            model_name="peerendpoint",
            old_name="role_new",
            new_name="role",
        ),
    ]
