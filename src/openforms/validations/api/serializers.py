from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class ValidationInputSerializer(serializers.Serializer):
    value = serializers.CharField(
        label=_("value"), help_text=_("Value to be validated")
    )


class ValidationRequestParamSerializer(serializers.Serializer):
    component = serializers.CharField()


class ValidationResultSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField(
        label=_("Is valid"), help_text=_("Boolean indicating value passed validation.")
    )
    messages = serializers.ListField(
        child=serializers.CharField(
            label=_("error message"),
            help_text=_("error message"),
        ),
        help_text=_("List of validation error messages for display."),
    )


class ValidationPluginSerializer(serializers.Serializer):
    id = serializers.CharField(
        source="identifier",
        label=_("ID"),
        help_text=_("The unique plugin identifier"),
    )
    label = serializers.CharField(
        source="verbose_name",
        label=_("Label"),
        help_text=_("The human-readable name for a plugin."),
    )
    components = serializers.ListField(
        label=_("Components"),
        help_text=_("The components for which the plugin is relevant."),
        child=serializers.CharField(),
    )
