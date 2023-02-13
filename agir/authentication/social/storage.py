from social_django.models import DjangoStorage, UserSocialAuth

from agir.people.models import Person


class AgirSocialUser(UserSocialAuth):
    def create_user(cls, *args, **kwargs):
        raise NotImplementedError("Cannot create user from social auth")

    @classmethod
    def get_users_by_email(cls, email):
        try:
            person = Person.objects.select_related("role").get(
                emails__address__iexact=email
            )
            person.ensure_role_exists()
            return [person.role]
        except Person.DoesNotExist:
            return []

    class Meta:
        proxy = True


class AgirDjangoStorage(DjangoStorage):
    user = AgirSocialUser
