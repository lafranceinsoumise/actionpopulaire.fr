from rest_framework import serializers

from agir.lib.utils import front_url


class TokTokUserSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="pk", read_only=True)
    displayName = serializers.CharField(source="display_name", read_only=True)
    isManager = serializers.SerializerMethodField(
        method_name="has_writing_access", read_only=True
    )
    groups = serializers.SerializerMethodField(read_only=True)

    def has_writing_access(self, person):
        return person.role.has_perm("toktok.access_data", person)

    def get_groups(self, person):
        return [
            {
                "id": group.id,
                "name": group.name,
                "uri": front_url("view_group", absolute=True, kwargs={"pk": group.id}),
            }
            for group in person.groups_with_active_membership
        ]
