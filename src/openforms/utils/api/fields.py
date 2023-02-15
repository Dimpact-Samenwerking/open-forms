from rest_framework import serializers


class PrimaryKeyRelatedAsChoicesField(serializers.PrimaryKeyRelatedField):
    """
    Custom subclass to register a custom drf-jsonschema-serializer converter.
    """

    pass
