from base64 import b64encode
from typing import BinaryIO, Literal, TypeAlias

from django.core.files.base import ContentFile

from zgw_consumers_ext.api_client import NLXClient

from .utils import get_today

DocumentStatus: TypeAlias = Literal[
    "in_bewerking",
    "ter_vaststelling",
    "definitief",
    "gearchiveerd",
]


class DocumentenClient(NLXClient):
    def create_document(
        self,
        informatieobjecttype: str,
        bronorganisatie: str,
        title: str,
        author: str,
        language: str,
        format: str,
        content: ContentFile | BinaryIO,
        status: DocumentStatus,
        filename: str,
        description: str = "",
        vertrouwelijkheidaanduiding: str = "",
    ):
        assert author, "author must be a non-empty string"
        today = get_today()
        file_content = content.read()
        base64_body = b64encode(file_content).decode()
        data = {
            "informatieobjecttype": informatieobjecttype,
            "bronorganisatie": bronorganisatie,
            "creatiedatum": today,
            "titel": title,
            "auteur": author,
            "taal": language,
            "formaat": format,
            "inhoud": base64_body,
            "status": status,
            "bestandsnaam": filename,
            "beschrijving": description,
            "indicatieGebruiksrecht": False,
            "bestandsomvang": (
                content.size if hasattr(content, "size") else len(file_content)
            ),
        }

        if vertrouwelijkheidaanduiding:
            data["vertrouwelijkheidaanduiding"] = vertrouwelijkheidaanduiding

        response = self.post("enkelvoudiginformatieobjecten", json=data)
        response.raise_for_status()

        return response.json()
