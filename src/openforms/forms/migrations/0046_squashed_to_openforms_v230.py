# Generated by Django 3.2.20 on 2023-09-08 10:56

import re

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import autoslug.fields
import tinymce.models

import csp_post_processor.fields
import openforms.forms.models.form_step
import openforms.registrations.fields
import openforms.template.validators


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0001_initial_pre_openforms_v230"),
        ("variables", "0001_initial_to_openforms_v230"),
    ]

    operations = [
        migrations.AddField(
            model_name="form",
            name="begin_text_en",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed at the start of the form to indicate the user can begin to fill in the form. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="begin text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="begin_text_nl",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed at the start of the form to indicate the user can begin to fill in the form. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="begin text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="change_text_en",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to change a certain step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="change text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="change_text_nl",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to change a certain step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="change text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="confirm_text_en",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to confirm the form is filled in correctly. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="confirm text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="confirm_text_nl",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to confirm the form is filled in correctly. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="confirm text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="explanation_template_en",
            field=csp_post_processor.fields.CSPPostProcessedWYSIWYGField(
                base_field=tinymce.models.HTMLField(
                    blank=True,
                    help_text="Content that will be shown on the start page of the form, below the title and above the log in text.",
                    verbose_name="explanation template",
                ),
                blank=True,
                help_text="Content that will be shown on the start page of the form, below the title and above the log in text.",
                null=True,
                verbose_name="explanation template",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="explanation_template_nl",
            field=csp_post_processor.fields.CSPPostProcessedWYSIWYGField(
                base_field=tinymce.models.HTMLField(
                    blank=True,
                    help_text="Content that will be shown on the start page of the form, below the title and above the log in text.",
                    verbose_name="explanation template",
                ),
                blank=True,
                help_text="Content that will be shown on the start page of the form, below the title and above the log in text.",
                null=True,
                verbose_name="explanation template",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="name_en",
            field=models.CharField(max_length=150, null=True, verbose_name="name"),
        ),
        migrations.AddField(
            model_name="form",
            name="name_nl",
            field=models.CharField(max_length=150, null=True, verbose_name="name"),
        ),
        migrations.AddField(
            model_name="form",
            name="previous_text_en",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to go to the previous step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="previous text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="previous_text_nl",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to go to the previous step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="previous text",
            ),
        ),
        migrations.AddField(
            model_name="formdefinition",
            name="name_en",
            field=models.CharField(max_length=50, null=True, verbose_name="name"),
        ),
        migrations.AddField(
            model_name="formdefinition",
            name="name_nl",
            field=models.CharField(max_length=50, null=True, verbose_name="name"),
        ),
        migrations.AddField(
            model_name="formstep",
            name="next_text_en",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to go to the next step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="step next text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="next_text_nl",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to go to the next step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="step next text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="previous_text_en",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to go to the previous step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="step previous text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="previous_text_nl",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to go to the previous step. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="step previous text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="save_text_en",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to save the current information. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="step save text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="save_text_nl",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to save the current information. Leave blank to get value from global configuration.",
                max_length=50,
                null=True,
                verbose_name="step save text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="translation_enabled",
            field=models.BooleanField(
                default=False, verbose_name="translation enabled"
            ),
        ),
        migrations.AlterField(
            model_name="formvariable",
            name="key",
            field=models.TextField(
                help_text="Key of the variable, should be unique with the form.",
                validators=[
                    django.core.validators.RegexValidator(
                        message="Invalid variable key. It must only contain alphanumeric characters, underscores, dots and dashes and should not be ended by dash or dot.",
                        regex=re.compile("^(\\w|\\w[\\w.\\-]*\\w)$"),
                    )
                ],
                verbose_name="key",
            ),
        ),
        migrations.AlterField(
            model_name="formvariable",
            name="data_type",
            field=models.CharField(
                choices=[
                    ("string", "String"),
                    ("boolean", "Boolean"),
                    ("object", "Object"),
                    ("array", "Array"),
                    ("int", "Integer"),
                    ("float", "Float"),
                    ("datetime", "Datetime"),
                    ("time", "Time"),
                    ("date", "Date"),
                ],
                help_text="The type of the value that will be associated with this variable",
                max_length=50,
                verbose_name="data type",
            ),
        ),
        migrations.AddField(
            model_name="formdefinition",
            name="component_translations",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Translations for literals used in components",
                verbose_name="Component translations",
            ),
        ),
        migrations.AddField(
            model_name="formlogic",
            name="description",
            field=models.CharField(
                blank=True,
                help_text="Logic rule description in natural language.",
                max_length=100,
                verbose_name="description",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="include_confirmation_page_content_in_pdf",
            field=models.BooleanField(
                default=True,
                help_text="Display the instruction from the confirmation page in the PDF.",
                verbose_name="include confirmation page content in PDF",
            ),
        ),
        migrations.AlterField(
            model_name="form",
            name="submission_confirmation_template",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="The content of the submission confirmation page. It can contain variables that will be templated from the submitted form data. If not specified, the global template will be used.",
                validators=[
                    openforms.template.validators.DjangoTemplateValidator(
                        backend="openforms.template.openforms_backend"
                    )
                ],
                verbose_name="submission confirmation template",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="submission_confirmation_template_en",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="The content of the submission confirmation page. It can contain variables that will be templated from the submitted form data. If not specified, the global template will be used.",
                null=True,
                validators=[
                    openforms.template.validators.DjangoTemplateValidator(
                        backend="openforms.template.openforms_backend"
                    )
                ],
                verbose_name="submission confirmation template",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="submission_confirmation_template_nl",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="The content of the submission confirmation page. It can contain variables that will be templated from the submitted form data. If not specified, the global template will be used.",
                null=True,
                validators=[
                    openforms.template.validators.DjangoTemplateValidator(
                        backend="openforms.template.openforms_backend"
                    )
                ],
                verbose_name="submission confirmation template",
            ),
        ),
        migrations.AlterField(
            model_name="formvariable",
            name="prefill_attribute",
            field=models.CharField(
                blank=True,
                help_text="Which attribute from the prefill response should be used to fill this variable",
                max_length=200,
                verbose_name="prefill attribute",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="appointment_enabled",
            field=models.BooleanField(
                default=False,
                help_text="This is experimental mode for appointments",
                verbose_name="appointment enabled",
            ),
        ),
        migrations.AddField(
            model_name="formvariable",
            name="service_fetch_configuration",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="variables.servicefetchconfiguration",
                verbose_name="service fetch configuration",
            ),
        ),
        migrations.AddConstraint(
            model_name="formvariable",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        models.Q(("prefill_plugin", ""), _negated=True),
                        ("service_fetch_configuration__isnull", False),
                    ),
                    _negated=True,
                ),
                name="prefill_config_xor_service_fetch_config",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="send_confirmation_email",
            field=models.BooleanField(
                default=True,
                help_text="Whether a confirmation email should be sent to the end user filling in the form.",
                verbose_name="send confirmation email",
            ),
        ),
        migrations.RemoveField(
            model_name="form",
            name="confirmation_email_option",
        ),
        migrations.AddField(
            model_name="form",
            name="suspension_allowed",
            field=models.BooleanField(
                default=True,
                help_text="Whether the user is allowed to suspend this form or not.",
                verbose_name="suspension allowed",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="authentication_backend_options",
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name="per form authentication backend config",
            ),
        ),
        migrations.RenameField(
            model_name="form",
            old_name="appointment_enabled",
            new_name="is_appointment",
        ),
        migrations.AlterField(
            model_name="form",
            name="is_appointment",
            field=models.BooleanField(
                default=False,
                help_text="Mark the form as an appointment form. Appointment forms do not support form designer steps.",
                verbose_name="appointment enabled",
            ),
        ),
        migrations.AddField(
            model_name="formvariable",
            name="prefill_identifier_role",
            field=models.CharField(
                choices=[("main", "Main"), ("authorised_person", "Authorised person")],
                default="main",
                help_text="In case that multiple identifiers are returned (in the case of eHerkenning bewindvoering and DigiD Machtigen), should the prefill data related to the main identifier be used, or that related to the authorised person?",
                max_length=100,
                verbose_name="prefill identifier role",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                editable=True,
                max_length=100,
                null=True,
                populate_from=openforms.forms.models.form_step.populate_from_form_definition_name,
                unique_with=("form",),
                verbose_name="slug",
            ),
        ),
        migrations.AddConstraint(
            model_name="formstep",
            constraint=models.UniqueConstraint(
                fields=("form", "slug"), name="form_slug_unique_together"
            ),
        ),
        migrations.AlterField(
            model_name="formdefinition",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                editable=True, max_length=100, populate_from="name", verbose_name="slug"
            ),
        ),
        migrations.CreateModel(
            name="FormRegistrationBackend",
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
                    "key",
                    models.CharField(
                        help_text="The key to use to refer to this configuration in form logic.",
                        max_length=50,
                        verbose_name="key",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="A recognisable name for this backend configuration.",
                        max_length=255,
                        verbose_name="name",
                    ),
                ),
                (
                    "backend",
                    openforms.registrations.fields.RegistrationBackendChoiceField(
                        max_length=100, verbose_name="registration backend"
                    ),
                ),
                (
                    "options",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        verbose_name="registration backend options",
                    ),
                ),
                (
                    "form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registration_backends",
                        to="forms.form",
                    ),
                ),
            ],
            options={
                "unique_together": {("form", "key")},
                "verbose_name": "registration backend",
                "verbose_name_plural": "registration backends",
            },
        ),
        migrations.RemoveField(
            model_name="form",
            name="registration_backend",
        ),
        migrations.RemoveField(
            model_name="form",
            name="registration_backend_options",
        ),
        migrations.AddField(
            model_name="form",
            name="ask_privacy_consent",
            field=models.CharField(
                choices=[
                    ("global_setting", "Global setting"),
                    ("required", "Required"),
                    ("disabled", "Disabled"),
                ],
                default="global_setting",
                help_text="If enabled, the user will have to agree to the privacy policy before submitting a form.",
                max_length=50,
                verbose_name="ask privacy consent",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="ask_statement_of_truth",
            field=models.CharField(
                choices=[
                    ("global_setting", "Global setting"),
                    ("required", "Required"),
                    ("disabled", "Disabled"),
                ],
                default="global_setting",
                help_text="If enabled, the user will have to agree that they filled out the form truthfully before submitting it.",
                max_length=50,
                verbose_name="ask statement of truth",
            ),
        ),
    ]
