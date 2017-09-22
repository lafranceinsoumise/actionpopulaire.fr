
class Scope(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __eq__(self, other_scope):
        return self.name == other_scope

view_profile = Scope('view_profile', 'Voir mon profil')
edit_profile = Scope('edit_profile', 'Changer mon profil')
edit_event = Scope('edit_event', 'Éditer mes événements')
edit_rsvp = Scope('edit_rsvp', 'Voir et éditer mes participations aux événements')
edit_supportgroup = Scope('edit_supportgroup', "Éditer mes groupes d'appui")
edit_membership = Scope('edit_membership', "Voir et éditer mes participations aux groups d'appui")
edit_authorization = Scope('edit_authorization', "Éditer mes autorisations d'accès")

scopes = [
    view_profile,
    edit_profile,
    edit_event,
    edit_rsvp,
    edit_supportgroup,
    edit_membership,
    edit_authorization,
]

scopes_name = [scope.name for scope in scopes]
