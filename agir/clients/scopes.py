
class Scope(object):
    def __init__(self, name, description, permissions):
        self.name = name
        self.description = description
        self.permissions = permissions

    def __eq__(self, other_scope):
        return self.name == other_scope


view_profile = Scope('view_profile', 'Voir mon profil', ['people.view_person'])
edit_profile = Scope('edit_profile', 'Changer mon profil', ['people.change_person'])
edit_event = Scope('edit_event', 'Éditer mes événements', ['events.change_event'])
edit_rsvp = Scope('edit_rsvp', 'Voir et éditer mes participations aux événements', [])
edit_supportgroup = Scope('edit_supportgroup', "Éditer mes groupes d'action", [])
edit_membership = Scope('edit_membership', "Voir et éditer mes participations aux groupes d'action", [])
edit_authorization = Scope('edit_authorization', "Éditer mes autorisations d'accès", [])

scopes = [
    view_profile,
    edit_profile,
    edit_event,
    edit_rsvp,
    edit_supportgroup,
    edit_membership,
    edit_authorization,
]

scopes_names = [scope.name for scope in scopes]


def get_required_scopes(permission):
    return [scope for scope in scopes if permission in scope.permissions]
