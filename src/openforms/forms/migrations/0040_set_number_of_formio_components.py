# Generated by Django 3.2.15 on 2022-08-11 14:20

from django.db import migrations

from openforms.forms.models.form_definition import _get_number_of_components


def set_number_of_components(apps, _):
    FormDefinition = apps.get_model("forms", "FormDefinition")
    for fd in FormDefinition.objects.exclude(configuration=None).filter(
        _num_components=0
    ):
        fd._num_components = _get_number_of_components(fd)
        fd.save(update_fields=["_num_components"])


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0039_formdefinition__num_components"),
    ]

    operations = [
        migrations.RunPython(set_number_of_components, migrations.RunPython.noop),
    ]
