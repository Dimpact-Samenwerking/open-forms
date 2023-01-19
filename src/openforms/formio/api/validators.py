from typing import Iterable, Optional

from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

import magic
from rest_framework import serializers


def mimetype_allowed(
    mime_type: str,
    allowed_regular_mime_types: Iterable[str],
    allowed_wildcard_mime_types: Iterable[str],
) -> bool:
    """
    Test if the file mime type passes the allowed_mime_types Formio configuration.

    The test for `allowed_regular_mime_types` is list inclusion. The test for
    `allowed_wildcard_mime_types` is string inclusion (is my string in
    `allowed_regular_mime_types` a substring of `mime_type`?).
    """
    #  no allowlist specified -> everything is allowed
    if not (allowed_regular_mime_types or allowed_wildcard_mime_types):
        return True

    # wildcard specified -> everything is allowed
    if "*" in allowed_wildcard_mime_types:
        return True

    # check1: is mimetype included in regular types?
    if mime_type in allowed_regular_mime_types:
        return True

    # check2: is the string mimetype a substring of any string in wildcard_mime_types?
    return any(
        mime_type.startswith(pattern[:-1]) for pattern in allowed_wildcard_mime_types
    )


class MimeTypeValidator:
    def __init__(self, allowed_mime_types: Optional[Iterable[str]] = None):
        self.any_allowed = allowed_mime_types is None

        allowed_mime_types = allowed_mime_types or []
        normalized = [
            item for string in allowed_mime_types for item in string.split(",")
        ]
        self._regular_mimes = [item for item in normalized if not item.endswith("*")]
        self._wildcard_mimes = [item for item in normalized if item.endswith("*")]

    def __call__(self, value: UploadedFile) -> None:
        head = value.read(2048)
        ext = value.name.split(".")[-1]
        mime_type = magic.from_buffer(head, mime=True)

        # gh #2520
        # application/x-ole-storage on Arch with shared-mime-info 2.0+155+gf4e7cbc-1
        if mime_type in ["application/CDFV2", "application/x-ole-storage"]:
            whole_file = head + value.read()
            mime_type = magic.from_buffer(whole_file, mime=True)

        if not (
            self.any_allowed
            or mimetype_allowed(mime_type, self._regular_mimes, self._wildcard_mimes)
        ):
            raise serializers.ValidationError(
                _("The file '{filename}' is not a valid file type.").format(
                    filename=value.name
                ),
            )

        # Contents is allowed. Do extension or submitted content_type agree?
        if value.content_type == "application/octet-stream":
            m = magic.Magic(extension=True)
            extensions = m.from_buffer(head).split("/")
            # magic db doesn't know any more specific extension(s), so accept the
            # file
            if extensions == ["???"]:
                return

            # we did find actual potential extensions, so we can validate the filename
            # by extension.

            # accept the file if the file extension is present in the extensions detected
            # by libmagic - this means the extension (likely) has not been tampered with
            if ext in extensions:
                return

            raise serializers.ValidationError(
                _("The file '{filename}' is not a {file_type}.").format(
                    filename=value.name, file_type=f".{ext}"
                )
            )
        elif mime_type != value.content_type:
            raise serializers.ValidationError(
                _("The file '{filename}' is not a {file_type}.").format(
                    filename=value.name, file_type=f".{ext}"
                )
            )
