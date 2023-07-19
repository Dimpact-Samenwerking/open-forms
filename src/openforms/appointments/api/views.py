import logging

from django.utils.translation import gettext_lazy as _

import elasticapm
from drf_spectacular.plumbing import build_array_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from openforms.api.authentication import AnonCSRFSessionAuthentication
from openforms.api.serializers import ExceptionSerializer, ValidationErrorSerializer
from openforms.api.views import ListMixin
from openforms.formio.api.schema import FORMIO_COMPONENT_SCHEMA
from openforms.logging import logevent
from openforms.submissions.api.mixins import SubmissionCompletionMixin
from openforms.submissions.api.permissions import (
    ActiveSubmissionPermission,
    AnyActiveSubmissionPermission,
)
from openforms.submissions.models import Submission

from ..base import Location, Product
from ..exceptions import AppointmentDeleteFailed, CancelAppointmentFailed
from ..models import Appointment, AppointmentsConfig
from ..utils import delete_appointment_for_submission, get_plugin
from .parsers import AppointmentCreateCamelCaseJSONParser
from .permissions import AppointmentCreatePermission
from .renderers import AppointmentCreateJSONRenderer
from .serializers import (
    AppointmentSerializer,
    CancelAppointmentInputSerializer,
    CustomerFieldsInputSerializer,
    DateInputSerializer,
    DateSerializer,
    LocationInputSerializer,
    LocationSerializer,
    ProductSerializer,
    TimeInputSerializer,
    TimeSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(
    summary=_("List available products"),
)
class ProductsListView(ListMixin, APIView):
    """
    List all products a user can choose when making an appointment.
    """

    authentication_classes = ()
    permission_classes = [AnyActiveSubmissionPermission]
    serializer_class = ProductSerializer

    def get_objects(self):
        plugin = get_plugin()
        config = AppointmentsConfig().get_solo()
        assert isinstance(config, AppointmentsConfig)
        kwargs = {}
        if location_id := config.limit_to_location:
            kwargs["location_id"] = location_id
        with elasticapm.capture_span(
            name="get-available-products", span_type="app.appointments.get_products"
        ):
            return plugin.get_available_products(**kwargs)


# The serializer + @extend_schema approach for querystring params is not ideal, the
# issue to refactor this is here: https://github.com/open-formulieren/open-forms/issues/611
@extend_schema(
    summary=_("List available locations for a given product"),
    parameters=[
        OpenApiParameter(
            "product_id",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description=_("ID of the product"),
            required=True,
        ),
    ],
)
class LocationsListView(ListMixin, APIView):
    """
    List all locations for a given product.

    Note that you must include valid querystring parameters to get actual results. If
    you don't, then an empty list is returned.
    """

    authentication_classes = ()
    permission_classes = [AnyActiveSubmissionPermission]
    serializer_class = LocationSerializer

    def get_objects(self):
        serializer = LocationInputSerializer(data=self.request.query_params)
        is_valid = serializer.is_valid()
        # TODO: ideally we want to use raise_exception=True, but the SDK and the way
        # that Formio work is that we can't prevent the invalid request from firing.
        # Instead, we just return an empty result list which populates dropdowns with
        # empty options.
        if not is_valid:
            return []

        product = Product(
            identifier=serializer.validated_data["product_id"], code="", name=""
        )

        plugin = get_plugin()
        with elasticapm.capture_span(
            name="get-available-locations", span_type="app.appointments.get_locations"
        ):
            return plugin.get_locations([product])


@extend_schema(
    summary=_("List available dates for a given location and product"),
    parameters=[
        OpenApiParameter(
            "product_id",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description=_("ID of the product"),
            required=True,
        ),
        OpenApiParameter(
            "location_id",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description=_("ID of the location"),
            required=True,
        ),
    ],
)
class DatesListView(ListMixin, APIView):
    """
    List all dates for a given product.

    Note that you must include valid querystring parameters to get actual results. If
    you don't, then an empty list is returned.
    """

    authentication_classes = ()
    permission_classes = [AnyActiveSubmissionPermission]
    serializer_class = DateSerializer

    def get_objects(self):
        serializer = DateInputSerializer(data=self.request.query_params)
        is_valid = serializer.is_valid()
        # TODO: ideally we want to use raise_exception=True, but the SDK and the way
        # that Formio work is that we can't prevent the invalid request from firing.
        # Instead, we just return an empty result list which populates dropdowns with
        # empty options.
        if not is_valid:
            return []

        product = Product(
            identifier=serializer.validated_data["product_id"], code="", name=""
        )
        location = Location(
            identifier=serializer.validated_data["location_id"], name=""
        )

        plugin = get_plugin()
        with elasticapm.capture_span(
            name="get-available-dates", span_type="app.appointments.get_dates"
        ):
            dates = plugin.get_dates([product], location)
        return [{"date": date} for date in dates]


@extend_schema(
    summary=_("List available times for a given location, product, and date"),
    parameters=[
        OpenApiParameter(
            "product_id",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description=_("ID of the product"),
            required=True,
        ),
        OpenApiParameter(
            "location_id",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description=_("ID of the location"),
            required=True,
        ),
        OpenApiParameter(
            "date",
            OpenApiTypes.DATE,
            OpenApiParameter.QUERY,
            description=_("The date"),
            required=True,
        ),
    ],
)
class TimesListView(ListMixin, APIView):
    """
    List all times for a given product.

    Note that you must include valid querystring parameters to get actual results. If
    you don't, then an empty list is returned.
    """

    authentication_classes = ()
    permission_classes = [AnyActiveSubmissionPermission]
    serializer_class = TimeSerializer

    def get_objects(self):
        serializer = TimeInputSerializer(data=self.request.query_params)
        is_valid = serializer.is_valid()
        # TODO: ideally we want to use raise_exception=True, but the SDK and the way
        # that Formio work is that we can't prevent the invalid request from firing.
        # Instead, we just return an empty result list which populates dropdowns with
        # empty options.
        if not is_valid:
            return []

        product = Product(
            identifier=serializer.validated_data["product_id"], code="", name=""
        )
        location = Location(
            identifier=serializer.validated_data["location_id"], name=""
        )

        plugin = get_plugin()
        with elasticapm.capture_span(
            name="get-available-times", span_type="app.appointments.get_times"
        ):
            times = plugin.get_times(
                [product], location, serializer.validated_data["date"]
            )
        return [{"time": time} for time in times]


@extend_schema(
    summary=_("Get required customer field details for a given product"),
    parameters=[
        OpenApiParameter(
            "product_id",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description=_("ID of the product, may be repeated for multiple products."),
            required=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=build_array_type(FORMIO_COMPONENT_SCHEMA, min_length=1),
            description=_("Customer fields list as Form.io components."),
        ),
        400: OpenApiResponse(
            response=ValidationErrorSerializer,
            description=_("Invalid input parameters."),
        ),
        403: OpenApiResponse(
            response=ExceptionSerializer,
            description=_("Insufficient permissions."),
        ),
    },
)
class RequiredCustomerFieldsListView(APIView):
    """
    Retrieve the customer fields required for the appointment.

    Note that this requires valid querystring parameters to get results. You will get
    an HTTP 400 on invalid input parameters.

    The required fields are returned as an array of Form.io component definitions,
    with ready to use component keys, labels and relevant validators.
    """

    authentication_classes = ()
    permission_classes = [AnyActiveSubmissionPermission]

    def get(self, request, *args, **kwargs):
        input_serializer = CustomerFieldsInputSerializer(data=self.request.query_params)
        input_serializer.is_valid(raise_exception=True)

        product = input_serializer.validated_data["product_id"]
        plugin = get_plugin()

        with elasticapm.capture_span(
            name="get-required-customer-fields",
            span_type="app.appointments.get_required_customer_fields",
        ):
            fields = plugin.get_required_customer_fields([product])

        return Response(fields)


@extend_schema(
    summary=_("Cancel an appointment"),
    request=CancelAppointmentInputSerializer,
    responses={
        204: None,
        403: OpenApiResponse(
            response=ExceptionSerializer,
            description=_("Unable to verify ownership of the appointment."),
        ),
        502: OpenApiResponse(
            response=ExceptionSerializer,
            description=_("Unable to cancel appointment."),
        ),
    },
)
class CancelAppointmentView(GenericAPIView):
    lookup_field = "uuid"
    lookup_url_kwarg = "submission_uuid"
    queryset = Submission.objects.all()
    authentication_classes = (AnonCSRFSessionAuthentication,)
    permission_classes = [ActiveSubmissionPermission]

    def post(self, request, *args, **kwargs):
        submission = self.get_object()
        plugin = get_plugin()

        logevent.appointment_cancel_start(submission.appointment_info, plugin)

        serializer = CancelAppointmentInputSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logevent.appointment_cancel_failure(submission.appointment_info, plugin, e)
            raise e

        emails = submission.get_email_confirmation_recipients(submission.data)

        # The user must enter the email address they used when creating
        # the appointment which we validate here
        if serializer.validated_data["email"] not in emails:
            e = PermissionDenied
            logevent.appointment_cancel_failure(submission.appointment_info, plugin, e)
            raise e

        try:
            delete_appointment_for_submission(submission, plugin)
        except AppointmentDeleteFailed as exc:
            raise CancelAppointmentFailed() from exc

        return Response(status=HTTP_204_NO_CONTENT)


@extend_schema(
    summary=_("Create an appointment"),
    responses={
        201: AppointmentSerializer,
        400: OpenApiResponse(
            response=ValidationErrorSerializer,
            description=_("Invalid submission data."),
        ),
        403: OpenApiResponse(
            response=ExceptionSerializer,
            description=_("Invalid or missing submission in session."),
        ),
        "5XX": OpenApiResponse(
            response=ExceptionSerializer,
            description=_("Unable to cancel appointment."),
        ),
    },
)
class CreateAppointmentView(SubmissionCompletionMixin, CreateAPIView):
    authentication_classes = (AnonCSRFSessionAuthentication,)
    permission_classes = [AnyActiveSubmissionPermission, AppointmentCreatePermission]
    serializer_class = AppointmentSerializer
    parser_classes = [AppointmentCreateCamelCaseJSONParser]
    renderer_classes = [AppointmentCreateJSONRenderer]

    def perform_create(self, serializer: AppointmentSerializer):
        super().perform_create(serializer)

        appointment: Appointment = serializer.instance  # type: ignore

        status_url = self._complete_submission(appointment.submission)
        # set the attribute so the response serializer can emit the status URL again
        serializer._status_url = status_url
