.. _developers_backend_core_submissions:

===========================
Core: submission processing
===========================

Once a form is submitted by the user, a number of actions take place to process
this submission. The complete process is shown below.

.. image:: _assets/submission_flow.png

Depending on the plugins that are active, some actions are skipped (boxes with
the dotted borders). Some actions are blocking but most actions have a fall
through mechanism to prevent the user from waiting for feedback for too long.

Globally, the various actions and plugin categories are processed in order:

#. If applicable, an :ref:`appointment <developers_appointment_plugins>` is
   created. If this fails, the submission is blocked and the user sees an error
   message and can try again.
#. Pre-registration step. Each :ref:`registration plugin <developers_registration_plugins>` can perform
   pre-registration task, like for example generating and setting a submission reference ID. If no registration backend
   is configured, then an internal ID is generated and set on the submission.
#. A PDF is created that the user can download.
   This PDF is also uploaded to most
   :ref:`registration backends <developers_registration_plugins>`, depending
   on the plugin.
#. If a :ref:`registration backend <developers_registration_plugins>` is configured, the submission is registered.
#. Post-registration step. Each :ref:`registration plugin <developers_registration_plugins>` can perform
   post-registration tasks like obtaining a registration ID from the external service and setting it on the submission.
   If a registration ID cannot be retrieved, an internal ID is used to not block the process.
   If an appointment was made, the appointment is updated with the ID.
#. The confirmation page is shown, containing appointment information if
   applicable and the registration or internal ID. If payment is due, a payment
   link is also shown to start the payment process.
#. If the user clicks on the payment link, the
   :ref:`payment process <developers_payment_plugins>` starts. If this process
   is not completed in a reasonable amount of time, it is assumed the user did
   not pay. If payment is completed within or after the timeout, the
   registration is updated with the payment status.
#. If no payment was required, or payment was completed, or the payment timeout
   was reached, a confirmation email is sent. Depending on all the results of
   the previous actions, the confirmation email shows different contents.

The confirmation email can show submission details, appointment details
(including links to cancel or change the appointment), payment details
(including a link to pay if not done so already) and custom information as part
of the form.
