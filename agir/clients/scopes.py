from oauth2_provider.scopes import BaseScopes


class Scope(object):
    def __init__(self, name, description, permissions):
        self.name = name
        self.description = description
        self.permissions = permissions

    def __eq__(self, other_scope):
        return self.name == other_scope


view_profile = Scope("view_profile", "Voir votre profil", ["people.view_person"])
edit_profile = Scope("edit_profile", "Changer votre profil", ["people.change_person"])
edit_event = Scope("edit_event", "Éditer vos événements", ["events.change_event"])
edit_rsvp = Scope("edit_rsvp", "Voir et éditer vos participations aux événements", [])
edit_supportgroup = Scope("edit_supportgroup", "Éditer vos groupes d'action", [])
view_membership = Scope(
    "view_membership", "Voir vos participations aux groupes d'action", permissions=[]
)
edit_membership = Scope(
    "edit_membership", "Éditer vos participations aux groupes d'action", []
)
edit_authorization = Scope("edit_authorization", "Éditer vos autorisations d'accès", [])
toktok = Scope(
    "toktok", "Accès aux informations nécessaires à l'application TokTok", []
)

scopes = [
    view_profile,
    edit_profile,
    edit_event,
    edit_rsvp,
    edit_supportgroup,
    view_membership,
    edit_membership,
    edit_authorization,
    toktok,
]

scopes_names = [scope.name for scope in scopes]


class ScopesBackend(BaseScopes):
    def get_all_scopes(self):
        return {scope.name: scope.description for scope in scopes}

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        if application is not None:
            return application.scopes

        return self.get_all_scopes()

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        return view_profile.name


def get_required_scopes(permission):
    return [scope for scope in scopes if permission in scope.permissions]
