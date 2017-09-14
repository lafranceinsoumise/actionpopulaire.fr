"""Collections of useful tags that are used as part as forms or API views

"""

from django.utils.translation import ugettext_lazy as _

from .models import PersonTag

__all__ = ["skills_tags", "action_tags"]


skills_tags = [
    ("info blogueur", _("Blogueur·se")),
    ("info bricoleur", _("Bricoleur·se")),
    ("info chauffeur", _("Chauffeur·se")),
    ("info cuisinier", _("Cuisinier·e")),
    ("info graphiste", _("Graphiste, infographiste, dessinateur·rice")),
    ("info informaticien", _("Informaticien·ne, développeur·se, jeux vidéo")),
    ("info journaliste", _("Journaliste")),
    ("info juriste", _("Juriste")),
    ("info éduc pop", _("Maîtrise des techniques d'éducation populaire et d'animation")),
    ("info technicien son lumière", _("Maîtrise son, lumière, électricien·ne")),
    ("info Facebook/Twitter", _("Maîtrise Facebook/Twitter")),
    ("info mécanicien", _("Mécanicien·ne")),
    ("info sécurité", _("Métiers de la sécurité")),
    ("info musicien", _("Musicien·ne")),
    ("info paysan", _("Paysan·ne, vigneron·ne")),
    ("info peintre", _("Peintre, graffeur·se")),
    ("info pilleur de banque", _("Pilleur·se de banque")),
    ("info écrivain", _("Professeur·e, écrivain·e, universitaire")),
    ("info secrétariat", _("Secrétariat, accueil téléphonique, gestion d'emploi du temps")),
    ("info vidéo", _("Vidéos, photos")),
    ("info veille", _("Veille télés et radios")),
]

action_tags = {
    'nearby': [
        (
            "agir localement",
            _("Agir près de chez vous"),
            _("Distribuer des tracts, coller des affiches, informer vos voisins, proches, collègues...")
        ),
        (
            "agir listes électorales",
            _("Inscrire des gens sur les listes électorales"),
            _("À chaque élection, plusieurs millions de personnes sont mal ou non inscrites sur les listes électorales et ne peuvent pas voter. Agissez pour changer cela.")
        ),
        (
            "agir accueil évènements",
            _("Accueillir de petits évènements chez vous "),
            _("Organiser une soirée, un apéro, une écoute collective d'une émission télé...")
        ),
        (
            "agir participation évènements",
            _("Participer à des évènements près de chez vous"),
            _("Être informé.e sur les évènements organisés près de chez vous.")
        ),
        (
            "agir groupe d'appui",
            _("Créer ou rejoindre un groupe d'appui près de chez vous "),
            _("Rencontrez des volontaires près de chez vous et agir avec eux.")
        ),
        (
            "agir JRI",
            _("Prendre des photos ou vidéos près de chez vous"),
            _("Filmer ou photographier des évènements locaux de la France insoumise.")
        )
    ],
    "internet": [
        (
            "agir appels",
            _("Participer aux campagnes d'appel"),
            _("Passer des appels téléphoniques depuis votre ordinateur. ")
        ),
        (
            "agir facebook",
            _("Agir sur Facebook"),
            _("Partager des publications, inviter vos ami.e.s, diffuser des informations...")
        ),
        (
            "agir twitter",
            _("Agir sur Twitter"),
            _("Partager des tweets, participer à des live-tweets d'émissions...")
        ),
        (
            "agir commentaires internet",
            _("Commenter des articles sur internet"),
            _("Utiliser les espaces de commentaire sur les sites de presse, les blogs ou les forums.")
        ),
        (
            "agir vidéos musiques",
            _("Proposer des vidéos et des musiques"),
            _("Réaliser des mini-reportages, zappings, chansons, fausses publicités, clips...")
        ),
        (
            "agir visuels",
            _("Proposer des visuels et des dessins"),
            _("Réaliser des infographies, slogans mis en images, caricatures...")
        ),
        (
            "agir blog",
            _("Utiliser votre blog pour faire connaître la France insoumise"),
            _("Faire un lien vers lafranceinsoumise.fr sur votre blog, faire connaître nos idées...")
        )
    ]
}


def ensure_tag_exist(tag, description):
    PersonTag.objects.update_or_create(
        label=tag,
        defaults={"description": description}
    )


# Ensure these tags exist and are up to date on startup
for tag, description in skills_tags:
    ensure_tag_exist(tag, description)

for tags in action_tags.values():
    for tag, title, description in tags:
        ensure_tag_exist(tag, f"{title} - {description}")
