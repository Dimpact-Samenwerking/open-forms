from django.db import models
from django.utils.translation import gettext_lazy as _

X_OF_CONTENT_TYPE_HEADER = "X-OF-Content-Type"
X_OF_CONTENT_UUID_HEADER = "X-OF-Content-UUID"
X_OF_EVENT_HEADER = "X-OF-Event"


class EmailEventChoices(models.TextChoices):
    registration = "registration", _("Registration")
    confirmation = "confirmation", _("Confirmation")
    cosign_confirmation = "cosign_confirmation", _("Co-sign confirmation")


class EmaiContentTypeChoices(models.TextChoices):
    submission = "submission.submission", _("Submission")
