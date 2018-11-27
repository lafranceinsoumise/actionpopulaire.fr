from rest_framework import serializers


class NBPersonWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = (
            "first_name",
            "last_name",
            "email",
            "email_opt_in",
            "id",
            "tags",
            "location",
        )
