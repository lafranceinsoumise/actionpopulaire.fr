from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user
from django.contrib.auth.context_processors import (
    PermWrapper as OriginalPermWrapper,
    PermLookupDict as OriginalPermLookupDict,
)

from agir.people.models import Person


class SpecificPermLookup:
    def __init__(self, user, app_label, perm_name):
        self.user = user
        self.app_label = app_label
        self.perm_name = perm_name

    def __contains__(self, obj=None):
        return self.user.has_perm("%s.%s" % (self.app_label, self.perm_name), obj=obj)

    def __bool__(self):
        return None in self


class PermLookupDict(OriginalPermLookupDict):
    def __getitem__(self, perm_name):
        return SpecificPermLookup(self.user, self.app_label, perm_name)


class PermWrapper(OriginalPermWrapper):
    def __getitem__(self, app_label):
        return PermLookupDict(self.user, app_label)


def get_person(request):
    user = get_user(request)
    if user.is_anonymous:
        return None

    try:
        return user.person
    except (AttributeError, Person.DoesNotExist):
        return None


def get_gender(request):
    person = get_person(request)

    if person is None:
        return ""

    return person.gender


def auth(request):
    """
    Renvoie des variables de contexte similaire à celles renvoyées par
    django.contrib.auth.context_processors.auth, mais en y rajoutant la
    possibilité de tester les permissions spécifiques à un objet.

    Pour cela, il faut tester si l'objet est "dans" la permission, par
    exemple :

        {% if obj in perms.app.view_model %}
    """

    return {
        "user": SimpleLazyObject(lambda: get_user(request)),
        "perms": SimpleLazyObject(lambda: PermWrapper(get_user(request))),
        "person": SimpleLazyObject(lambda: get_person(request)),
        "gender": SimpleLazyObject(lambda: get_person(request).gender),
    }
