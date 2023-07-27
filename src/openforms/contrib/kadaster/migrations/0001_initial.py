# Generated by Django 3.2.20 on 2023-07-25 13:41

from django.db import migrations, models
import django.db.models.deletion
import openforms.contrib.kadaster.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("zgw_consumers", "0019_alter_service_uuid"),
    ]

    operations = [
        migrations.CreateModel(
            name="KadasterApiConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "kadaster_service",
                    models.OneToOneField(
                        default=openforms.contrib.kadaster.models.get_default_kadaster_service,
                        limit_choices_to={"api_type": "orc"},
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="zgw_consumers.service",
                        verbose_name="Kadaster API",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kadaster API configuration",
            },
        ),
    ]
