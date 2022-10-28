import uuid
from unittest.mock import Mock, patch

from django.contrib.auth import SESSION_KEY
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from openforms.accounts.tests.factories import StaffUserFactory
from openforms.submissions.tests.factories import SubmissionFactory
from openforms.submissions.tests.mixins import SubmissionsMixin

from ...constants import (
    FORM_AUTH_SESSION_KEY,
    REGISTRATOR_SUBJECT_SESSION_KEY,
    AuthAttribute,
)
from ...registry import Registry
from ...tests.factories import RegistratorInfoFactory
from ...tests.test_registry import Plugin


class SubmissionLogoutTest(SubmissionsMixin, APITestCase):
    def test_logout_requires_submission_in_session(self):
        with self.subTest("fails when submission does not exist"):
            url = reverse("api:submission-logout", kwargs={"uuid": uuid.uuid4()})
            response = self.client.delete(url)
            self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        submission = SubmissionFactory.create(
            completed=False, auth_info__value="000000000"
        )
        url = reverse("api:submission-logout", kwargs={"uuid": submission.uuid})

        with self.subTest("fails when submission not in session"):
            response = self.client.delete(url)
            self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        with self.subTest("success when submission in session"):
            # now add it
            self._add_submission_to_session(submission)
            response = self.client.delete(url)
            self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_logout(self):
        register = Registry()

        register("plugin1")(Plugin)
        plugin1 = register["plugin1"]
        plugin1.provides_auth = AuthAttribute.bsn
        logout_mock = Mock()
        plugin1.logout = logout_mock

        # login admin user
        user = StaffUserFactory.create()
        self.client.force_login(user=user)

        # login form user
        session = self.client.session
        session[FORM_AUTH_SESSION_KEY] = {
            "plugin": "test",
            "attribute": AuthAttribute.bsn,
            "value": "000000000",
        }
        session.save()

        login_submission = SubmissionFactory.create(
            completed=False, auth_info__value="000000000", auth_info__plugin="plugin1"
        )
        other_submission = SubmissionFactory.create(
            completed=False, auth_info__value="000000000", auth_info__plugin="plugin1"
        )

        self._add_submission_to_session(login_submission)
        self._add_submission_to_session(other_submission)

        # call the endpoint
        url = reverse("api:submission-logout", kwargs={"uuid": login_submission.uuid})
        with patch("openforms.authentication.api.views.register", register):
            response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        login_submission.refresh_from_db()
        other_submission.refresh_from_db()

        # only login_submission is removed
        uuids = self._get_session_submission_uuids()
        self.assertNotIn(str(login_submission.uuid), uuids)
        self.assertIn(str(other_submission.uuid), uuids)

        # check that the submission is hashed
        self.assertNotEqual(login_submission.auth_info.value, "")
        self.assertNotEqual(login_submission.auth_info.value, "000000000")
        self.assertTrue(login_submission.auth_info.attribute_hashed)

        self.assertNotIn(FORM_AUTH_SESSION_KEY, self.client.session)

        # called logout() on the plugins
        logout_mock.assert_called()

        # admin user still authenticated
        self.assertIn(SESSION_KEY, session)

    def test_logout_non_existing_plugin(self):
        register = Registry()

        submission = SubmissionFactory.create(
            completed=False,
            auth_info__value="000000000",
            auth_info__plugin="non_existing_plugin",
        )
        RegistratorInfoFactory(submission=submission, plugin="non_existing_plugin")

        self._add_submission_to_session(submission)

        self.assertTrue(submission.is_authenticated)

        session = self.client.session
        session[FORM_AUTH_SESSION_KEY] = {
            "plugin": "test",
            "attribute": AuthAttribute.bsn,
            "value": "000000000",
        }
        session[REGISTRATOR_SUBJECT_SESSION_KEY] = {
            "attribute": AuthAttribute.bsn,
            "value": "000000000",
        }
        session.save()

        # call the endpoint
        url = reverse("api:submission-logout", kwargs={"uuid": submission.uuid})
        with patch("openforms.authentication.api.views.register", register):
            response = self.client.delete(url)

        # no error
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        # reload data
        submission.refresh_from_db()
        session = self.client.session

        self.assertTrue(submission.auth_info.attribute_hashed)
        self.assertTrue(submission.registrator.attribute_hashed)

        self.assertNotIn(FORM_AUTH_SESSION_KEY, session)
        self.assertNotIn(REGISTRATOR_SUBJECT_SESSION_KEY, session)
