from datetime import datetime
from typing import Any, Dict

from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from freezegun import freeze_time
from rest_framework.test import APIRequestFactory

from openforms.submissions.tests.factories import SubmissionFactory
from openforms.variables.service import get_static_variables

from ...service import FormioConfigurationWrapper, get_dynamic_configuration
from ...typing import DatetimeComponent

request_factory = APIRequestFactory()


@override_settings(TIME_ZONE="Europe/Amsterdam")
class DynamicDatetimeConfigurationTests(SimpleTestCase):
    @staticmethod
    def _get_dynamic_config(
        component: DatetimeComponent, variables: Dict[str, Any]
    ) -> DatetimeComponent:
        config_wrapper = FormioConfigurationWrapper({"components": [component]})
        request = request_factory.get("/irrelevant")
        submission = SubmissionFactory.build()
        static_vars = get_static_variables(submission=None)  # don't do queries
        variables.update({var.key: var.initial_value for var in static_vars})
        config_wrapper = get_dynamic_configuration(
            config_wrapper, request=request, submission=submission, data=variables
        )
        new_configuration = config_wrapper.configuration
        return new_configuration["components"][0]

    def test_validation_fixed_value_legacy_configuration(self):
        # legacy configuration = without the openForms.minDate keys etc.
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "datePicker": {
                "minDate": None,
                "maxDate": "2022-09-08T00:00:00+02:00",
            },
        }

        new_component = self._get_dynamic_config(component, {})

        self.assertIsNone(new_component["datePicker"]["minDate"])
        self.assertEqual(
            new_component["datePicker"]["maxDate"], "2022-09-08T00:00:00+02:00"
        )

    def test_min_max_datetime_fixed_value(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "minDate": {"mode": "fixedValue"},
                "maxDate": {"mode": "fixedValue"},
            },
            "datePicker": {
                "minDate": None,
                "maxDate": "2022-09-08T00:00:00+02:00",
            },
        }

        new_component = self._get_dynamic_config(component, {})

        self.assertIsNone(new_component["datePicker"]["minDate"])
        self.assertEqual(
            new_component["datePicker"]["maxDate"], "2022-09-08T00:00:00+02:00"
        )

    @freeze_time("2022-09-12T14:07:00Z")
    def test_min_datetime_future(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {"minDate": {"mode": "future"}},
            "datePicker": {"minDate": None},
        }

        new_component = self._get_dynamic_config(component, {})

        self.assertEqual(
            new_component["datePicker"]["minDate"], "2022-09-12T16:07:00+02:00"
        )

    @freeze_time("2022-09-12T14:07:00Z")
    def test_max_datetime_past(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {"maxDate": {"mode": "past"}},
            "datePicker": {"maxDate": None},
        }

        new_component = self._get_dynamic_config(component, {})

        self.assertEqual(
            new_component["datePicker"]["maxDate"],
            "2022-09-12T16:07:00+02:00",
        )

    @freeze_time("2022-10-03T12:00:00Z")
    def test_relative_to_variable_blank_delta(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "minDate": {
                    "mode": "relativeToVariable",
                    "variable": "now",
                    "operator": "",
                    "delta": {
                        "days": None,
                        "months": None,
                        # "years": None,  omitted deliberately - backend must handle missing keys
                    },
                },
            },
        }

        new_component = self._get_dynamic_config(component, {})

        self.assertEqual(
            new_component["datePicker"]["minDate"], "2022-10-03T14:00:00+02:00"
        )

    @freeze_time("2022-11-03T12:00:00Z")
    def test_relative_to_variable_blank_delta_dst_over(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "minDate": {
                    "mode": "relativeToVariable",
                    "variable": "now",
                    "operator": "",
                    "delta": {
                        "days": None,
                        "months": None,
                        # "years": None,  omitted deliberately - backend must handle missing keys
                    },
                },
            },
        }

        new_component = self._get_dynamic_config(component, {})

        self.assertEqual(
            new_component["datePicker"]["minDate"], "2022-11-03T13:00:00+01:00"
        )

    def test_relative_to_variable_add_delta(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "minDate": {
                    "mode": "relativeToVariable",
                    "variable": "someDatetime",
                    "operator": "add",
                    "delta": {
                        "days": 21,
                        "months": None,
                    },
                },
            },
        }
        # Amsterdam time
        some_date = timezone.make_aware(datetime(2022, 10, 14, 15, 0, 0))
        assert some_date.tzinfo.zone == "Europe/Amsterdam"

        new_component = self._get_dynamic_config(component, {"someDatetime": some_date})

        self.assertEqual(
            new_component["datePicker"]["minDate"],
            "2022-11-04T14:00:00+01:00",  # Nov. 4th Amsterdam time, where DST has ended
        )

    def test_relative_to_variable_subtract_delta(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "maxDate": {
                    "mode": "relativeToVariable",
                    "variable": "someDatetime",
                    "operator": "subtract",
                    "delta": {
                        "months": 1,
                    },
                },
            },
        }
        # Amsterdam time
        some_date = timezone.make_aware(datetime(2022, 10, 14, 15, 0, 0))
        assert some_date.tzinfo.zone == "Europe/Amsterdam"

        new_component = self._get_dynamic_config(component, {"someDatetime": some_date})

        self.assertEqual(
            new_component["datePicker"]["maxDate"], "2022-09-14T15:00:00+02:00"
        )

    def test_variable_empty_or_none(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "maxDate": {
                    "mode": "relativeToVariable",
                    "variable": "emptyVar",
                    "operator": "add",
                },
            },
        }
        empty_values = [None, ""]

        for empty_value in empty_values:
            with self.subTest(empty_value=empty_value):
                new_component = self._get_dynamic_config(
                    component, {"emptyVar": empty_value}
                )

                self.assertIsNone(new_component["datePicker"]["maxDate"])

    @freeze_time("2022-11-03T12:00:05.12345Z")
    def test_seconds_microseconds_are_truncated(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "minDate": {
                    "mode": "relativeToVariable",
                    "variable": "now",
                    "operator": "add",
                    "delta": {
                        "days": 0,
                        "months": 0,
                        "years": 0,
                    },
                },
            },
        }

        new_component = self._get_dynamic_config(component, {})

        self.assertEqual(
            new_component["datePicker"]["minDate"], "2022-11-03T13:00:00+01:00"
        )

    def test_variable_of_wrong_type_string(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "maxDate": {
                    "mode": "relativeToVariable",
                    "variable": "wrongVar",
                    "operator": "add",
                },
            },
        }

        with self.assertRaises(ValueError):
            self._get_dynamic_config(component, {"wrongVar": "Im not a datetime!! :("})

    def test_variable_string_datetime(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "maxDate": {
                    "mode": "relativeToVariable",
                    "variable": "stringDateVar",
                    "operator": "add",
                    "delta": {
                        "days": 0,
                        "months": 0,
                        "years": 0,
                    },
                },
            },
        }

        new_component = self._get_dynamic_config(
            component, {"stringDateVar": "2023-01-30T15:22:00+01:00"}
        )

        self.assertEqual(
            new_component["datePicker"]["maxDate"], "2023-01-30T15:22:00+01:00"
        )

    def test_variable_of_wrong_type_list(self):
        component = {
            "type": "datetime",
            "key": "aDatetime",
            "openForms": {
                "maxDate": {
                    "mode": "relativeToVariable",
                    "variable": "wrongVar",
                    "operator": "add",
                },
            },
        }

        with self.assertRaises(ValueError):
            self._get_dynamic_config(
                component, {"wrongVar": ["Im not a datetime!! :("]}
            )
