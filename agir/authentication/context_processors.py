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


def auth(request):
    """
    Renvoie des variables de contexte similaire à celles renvoyées par
    django.contrib.auth.context_processors.auth, mais en y rajoutant la
    possibilité de tester les permissions spécifiques à un objet.

    Pour cela, il faut tester si l'objet est "dans" la permission, par
    exemple :

        {% if obj in perms.app.view_model %}
    """

    if hasattr(request, "user"):
        user = request.user
        try:
            person = user.person
        except (AttributeError, Person.DoesNotExist):
            person = None

        gender = person.gender if person else "O"
    else:
        from django.contrib.auth.models import AnonymousUser

        user = AnonymousUser()
        person = None
        gender = "O"

    return {
        "user": user,
        "perms": PermWrapper(user),
        "person": person,
        "gender": gender,
    }
