from typing import TYPE_CHECKING, Optional

from django.utils.translation import gettext_lazy as _

from openforms.variables.base import BaseStaticVariable
from openforms.variables.constants import FormVariableDataTypes
from openforms.variables.registry import register_static_variable

from ..constants import AuthAttribute

if TYPE_CHECKING:  # pragma: nocover
    from openforms.submissions.models import Submission

    from ..utils import FormAuth


@register_static_variable("auth")
class Auth(BaseStaticVariable):
    name = _("Authentication")
    data_type = FormVariableDataTypes.object

    def get_initial_value(
        self, submission: Optional["Submission"]
    ) -> Optional["FormAuth"]:
        if not submission or not submission.is_authenticated:
            return None

        from ..utils import FormAuth

        auth_data = FormAuth(
            plugin=submission.auth_info.plugin,
            attribute=submission.auth_info.attribute,
            value=submission.auth_info.value,
            # TODO what is the structure of the data in the machtigen field?
            machtigen=submission.auth_info.machtigen,
        )

        return auth_data


def get_auth_value(submission: Optional["Submission"], attribute: str) -> str:
    if not submission or not submission.is_authenticated:
        return ""

    if submission.auth_info.attribute == attribute:
        return submission.auth_info.value

    return ""


@register_static_variable("auth_bsn")
class AuthBSN(BaseStaticVariable):
    name = _("Authentication BSN")
    data_type = FormVariableDataTypes.string

    @staticmethod
    def get_initial_value(submission: Optional["Submission"]) -> str:
        return get_auth_value(submission, AuthAttribute.bsn)


@register_static_variable("auth_kvk")
class AuthKvK(BaseStaticVariable):
    name = _("Authentication KvK")
    data_type = FormVariableDataTypes.string

    @staticmethod
    def get_initial_value(submission: Optional["Submission"]) -> str:
        return get_auth_value(submission, AuthAttribute.kvk)


@register_static_variable("auth_pseudo")
class AuthPseudo(BaseStaticVariable):
    name = _("Authentication pseudo")
    data_type = FormVariableDataTypes.string

    @staticmethod
    def get_initial_value(submission: Optional["Submission"]) -> str:
        return get_auth_value(submission, AuthAttribute.pseudo)
