# Generated by Django 3.2.20 on 2023-08-25 14:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forms", "0090_auto_20230816_1106"),
    ]

    operations = [
        migrations.AddField(
            model_name="form",
            name="activate_on",
            field=models.DateTimeField(
                blank=True,
                help_text="Date and time that the form should be activated.",
                null=True,
                verbose_name="activate on",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="deactivate_on",
            field=models.DateTimeField(
                blank=True,
                help_text="Date and time that the form should be deactivated.",
                null=True,
                verbose_name="deactivate on",
            ),
        ),
    ]
