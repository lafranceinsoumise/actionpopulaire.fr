from rest_framework import serializers

from agir.municipales.models import CommunePage


class CommunePageSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = CommunePage
        fields = ("name", "code_departement", "url")
