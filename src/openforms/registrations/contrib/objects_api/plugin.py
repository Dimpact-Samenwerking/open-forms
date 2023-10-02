import json
import sys
from datetime import date
from typing import Any, Dict, NoReturn

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from openforms.contrib.zgw.clients import DocumentenClient
from openforms.contrib.zgw.service import (
    create_attachment_document,
    create_csv_document,
    create_report_document,
)
from openforms.submissions.exports import create_submission_export
from openforms.submissions.mapping import SKIP, FieldConf, apply_data_mapping
from openforms.submissions.models import Submission, SubmissionReport
from openforms.submissions.public_references import set_submission_reference
from openforms.template import openforms_backend, render_from_string
from openforms.translations.utils import to_iso639_2b
from openforms.variables.utils import get_variables_for_context

from ...base import BasePlugin
from ...constants import REGISTRATION_ATTRIBUTE, RegistrationAttribute
from ...exceptions import NoSubmissionReference
from ...registry import register
from .checks import check_config
from .client import get_documents_client, get_objects_client
from .config import ObjectsAPIOptionsSerializer
from .models import ObjectsAPIConfig

PLUGIN_IDENTIFIER = "objects_api"


def _point_coordinate(value):
    if not value or not isinstance(value, list) or len(value) != 2:
        return SKIP
    return {"type": "Point", "coordinates": [value[0], value[1]]}


def build_options(plugin_options: dict, key_mapping: dict) -> dict:
    """
    Construct options from plugin options dict, allowing renaming of keys
    """
    options = {
        new_key: plugin_options[key_in_opts]
        for new_key, key_in_opts in key_mapping.items()
        if key_in_opts in plugin_options
    }
    return options


@register(PLUGIN_IDENTIFIER)
class ObjectsAPIRegistration(BasePlugin):
    verbose_name = _("Objects API registration")
    configuration_options = ObjectsAPIOptionsSerializer

    object_mapping = {
        "record.geometry": FieldConf(
            RegistrationAttribute.locatie_coordinaat, transform=_point_coordinate
        ),
    }

    def register_submission(
        self, submission: Submission, options: dict
    ) -> Dict[str, Any]:
        """Register a submission using the ObjectsAPI backend

        The creation of submission documents (report, attachment, csv) makes use of ZGW
        service functions (e.g. :func:`create_report_document`) and involves a mapping
        (and in some cases renaming) of variables which would otherwise not be
        accessible from here. For example, 'vertrouwelijkheidaanduiding' must be named
        'doc_vertrouwelijkheidaanduiding' because this is what the ZGW service functions
        use."""
        config = ObjectsAPIConfig.get_solo()
        assert isinstance(config, ObjectsAPIConfig)
        config.apply_defaults_to(options)

        # Prepare all documents to relate to the Objects API record
        with get_documents_client() as documents_client:
            # TODO: refactor this once zgw registration is updated for new clients too
            get_drc = lambda: documents_client

            # Create the document for the PDF summary
            submission_report = SubmissionReport.objects.get(submission=submission)
            submission_report_options = build_options(
                options,
                {
                    "informatieobjecttype": "informatieobjecttype_submission_report",
                    "organisatie_rsin": "organisatie_rsin",
                    "doc_vertrouwelijkheidaanduiding": "doc_vertrouwelijkheidaanduiding",
                },
            )

            document = create_report_document(
                submission.form.admin_name,
                submission_report,
                submission_report_options,
                get_drc=get_drc,
            )

            # Register the attachments
            # TODO turn attachments into dictionary when giving users more options then
            # just urls.
            attachments = []
            for attachment in submission.attachments:
                attachment_options = build_options(
                    options,
                    {
                        "informatieobjecttype": "informatieobjecttype_attachment",  # Different IOT than for the report
                        "organisatie_rsin": "organisatie_rsin",
                        "doc_vertrouwelijkheidaanduiding": "doc_vertrouwelijkheidaanduiding",
                    },
                )

                component_overwrites = {
                    "doc_vertrouwelijkheidaanduiding": attachment.doc_vertrouwelijkheidaanduiding,
                    "titel": attachment.titel,
                    "organisatie_rsin": attachment.bronorganisatie,
                    "informatieobjecttype": attachment.informatieobjecttype,
                }

                for key, value in component_overwrites.items():
                    if value:
                        attachment_options[key] = value

                attachment_document = create_attachment_document(
                    submission.form.admin_name,
                    attachment,
                    attachment_options,
                    get_drc=get_drc,
                )
                attachments.append(attachment_document["url"])

            # Create the CSV submission export, if requested.
            # If no CSV is being uploaded, then `assert csv_url == ""` applies.
            csv_url = register_submission_csv(submission, options, documents_client)

        # Prepare the submission data for sending it to the Objects API. This requires
        # rendering the configured JSON template and running some basic checks for
        # security and validity, before throwing it over the fence to the Objects API.

        context = {
            "_submission": submission,
            "productaanvraag_type": options["productaanvraag_type"],
            "variables": get_variables_for_context(submission),
            # Github issue #661, nested for namespacing note: other templates and context expose all submission
            # variables in the top level namespace, but that is due for refactor
            "submission": {
                "public_reference": submission.public_registration_reference,
                "kenmerk": str(submission.uuid),
                "language_code": submission.language_code,
                "uploaded_attachment_urls": attachments,
                "pdf_url": document["url"],
                "csv_url": csv_url,
            },
        }

        # FIXME: replace with better suited alternative dealing with JSON specifically
        record_data = render_from_string(
            options["content_json"],
            context=context,
            disable_autoescape=True,
            backend=openforms_backend,
        )

        if (
            data_size := sys.getsizeof(record_data)
        ) > settings.MAX_UNTRUSTED_JSON_PARSE_SIZE:
            formatted_size = filesizeformat(data_size)
            max_size = filesizeformat(settings.MAX_UNTRUSTED_JSON_PARSE_SIZE)
            raise SuspiciousOperation(
                f"Templated out content JSON exceeds the maximum size {max_size} ("
                f"it is {formatted_size})."
            )

        try:
            record_data = json.loads(record_data)
        except json.decoder.JSONDecodeError as err:
            raise RuntimeError(
                "Template evaluation did not result in valid JSON"
            ) from err

        object_data = {
            "type": options["objecttype"],
            "record": {
                "typeVersion": options["objecttype_version"],
                "data": record_data,
                # FIXME: do this based on appropriate timezone instead of using the naive
                # datetime.date. This works as long as servers are in the Europe/Amsterdam
                # timezone.
                "startAt": date.today().isoformat(),
            },
        }
        apply_data_mapping(
            submission, self.object_mapping, REGISTRATION_ATTRIBUTE, object_data
        )

        # Finally, send it over the wire to the Objects API
        with get_objects_client() as objects_client:
            response = objects_client.post("objects", json=object_data)
            response.raise_for_status()

        return response.json()

    def get_reference_from_result(self, result: None) -> NoReturn:
        raise NoSubmissionReference("Object API plugin does not emit a reference")

    def check_config(self):
        check_config()

    def get_config_actions(self):
        return [
            (
                _("Configuration"),
                reverse(
                    "admin:registrations_objects_api_objectsapiconfig_change",
                    args=(ObjectsAPIConfig.singleton_instance_id,),
                ),
            ),
        ]

    def pre_register_submission(self, submission: "Submission", options: dict) -> None:
        set_submission_reference(submission)

    def get_custom_templatetags_libraries(self) -> list[str]:
        prefix = "openforms.registrations.contrib.objects_api.templatetags.registrations.contrib"
        return [
            f"{prefix}.objects_api.json_tags",
        ]


def register_submission_csv(
    submission: Submission,
    options: dict,
    documents_client: DocumentenClient,
) -> str:
    if not options.get("upload_submission_csv", False):
        return ""

    if not options["informatieobjecttype_submission_csv"]:
        return ""

    submission_csv_options = build_options(
        options,
        {
            "informatieobjecttype": "informatieobjecttype_submission_csv",
            "organisatie_rsin": "organisatie_rsin",
            "doc_vertrouwelijkheidaanduiding": "doc_vertrouwelijkheidaanduiding",
            "auteur": "auteur",
        },
    )
    qs = Submission.objects.filter(pk=submission.pk).select_related("auth_info")
    submission_csv = create_submission_export(qs).export("csv")  # type: ignore

    language_code_2b = to_iso639_2b(submission.language_code)
    submission_csv_document = create_csv_document(
        f"{submission.form.admin_name} (csv)",
        submission_csv,
        submission_csv_options,
        # TODO: refactor this once zgw registration is updated for new clients too
        get_drc=lambda: documents_client,
        language=language_code_2b,
    )

    return submission_csv_document["url"]
