from .models import Role


class GetRoleMixin:
    prefetch = []

    def get_user(self, user_id):
        queryset = Role.objects.all()

        if self.prefetch:
            queryset = queryset.select_related(*self.prefetch)

        try:
            return queryset.get(pk=user_id)
        except Role.DoesNotExist:
            return None
