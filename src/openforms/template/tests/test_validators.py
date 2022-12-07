from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from ..validators import DjangoTemplateValidator


class DjangoTemplateValidatorTest(SimpleTestCase):
    def test_template_syntax(self):
        validator = DjangoTemplateValidator()

        valid = [
            "",
            " \n \n ",
            "aa",
            "{{ aa }}",
            '{% load i18n %}<p>{% trans "foo" %} {% if aa %}{{ aa.bb.cc }}{% endif %}</p>',
            # note: in-complete tags are acceptable to the template language
            "{{ aa }",
            "{% foo %",
        ]
        for text in valid:
            with self.subTest(f"valid: {text}"):
                validator(text)

        invalid = [
            ("{{{}}}", "Could not parse the remainder:"),
            ("{% if %}", "Unexpected end of expression in if tag."),
            ("{% foo %}", "Invalid block tag on line 1:"),
            ("{% $$ %}", "Invalid block tag on line 1:"),
        ]
        for text, message in invalid:
            with self.subTest(f"invalid: {text}"):
                with self.assertRaisesRegex(ValidationError, message):
                    validator(text)

    def test_required_tags(self):
        validator = DjangoTemplateValidator(required_template_tags=["csrf_token"])

        valid = [
            "{% csrf_token %}",
            "{%csrf_token %}",
            "{% csrf_token%}",
            "{%csrf_token%}",
            "{% load i18n %} aa {% csrf_token %} {{ aa.bb.cc }}",
        ]
        for text in valid:
            with self.subTest(f"valid: {text}"):
                validator(text)

        invalid = [
            (
                "",
                _("Missing required template-tag {tag}").format(
                    tag=r"\{% csrf_token %}"
                ),
            ),
            (
                "{% load i18n %} aa {{ aa.bb.cc }}",
                _("Missing required template-tag {tag}").format(
                    tag=r"\{% csrf_token %}"
                ),
            ),
        ]
        for text, message in invalid:
            with self.subTest(f"invalid: {text}"):
                with self.assertRaisesRegex(ValidationError, message):
                    validator(text)
