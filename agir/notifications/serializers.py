from rest_framework import serializers


class ParametersSerializer(serializers.Serializer):
    length = serializers.IntegerField(min_value=5, max_value=100, default=5)
    offset = serializers.IntegerField(min_value=0, default=0)
