from .models import Role


class GetRoleMixin:
    prefetch = []

    def get_user(self, user_id):
        queryset = Role.objects.all()

        if self.prefetch:
            queryset = queryset.select_related(*self.prefetch)

        try:
            role = queryset.get(pk=user_id)
            return role if self.user_can_authenticate(role) else None
        except Role.DoesNotExist:
            return None

    def user_can_authenticate(self, role):
        return role.is_active
