from django.db import migrations

info_tags = [
    ("blogueur", "Blogueur·se"),
    ("bricoleur", "Bricoleur·se"),
    ("chauffeur", "Chauffeur·se"),
    ("cuisinier", "Cuisinier·e"),
    ("graphiste", "Graphiste, infographiste, dessinateur·rice"),
    ("informaticien", "Informaticien·ne, développeur·se, jeux vidéo"),
    ("journaliste", "Journaliste"),
    ("juriste", "Juriste"),
    ("éduc pop", "Maîtrise des techniques d'éducation populaire et d'animation"),
    ("technicien son lumière", "Maîtrise son, lumière, électricien·ne"),
    ("Facebook/Twitter", "Maîtrise Facebook/Twitter"),
    ("mécanicien", "Mécanicien·ne"),
    ("sécurité", "Métiers de la sécurité"),
    ("musicien", "Musicien·ne"),
    ("paysan", "Paysan·ne, vigneron·ne"),
    ("peintre", "Peintre, graffeur·se"),
    ("pilleur de banque", "Pilleur·se de banque"),
    ("écrivain", "Professeur·e, écrivain·e, universitaire"),
    ("vidéo", "Vidéos, photos"),
    ("veille", "Veille télés et radios"),
]

agir_tags = [
    (
        "groupe d'appui",
        "Créer ou rejoindre un groupe d'appui près de chez vous",
        "Rencontrez des volontaires près de chez vous et agir avec eux.",
    ),
    (
        "localement",
        "Agir près de chez vous",
        "Distribuer des tracts, coller des affiches, informer vos voisins, proches, collègues...",
    ),
    (
        "listes électorales",
        "Inscrire des gens sur les listes électorales",
        "À chaque élection, plusieurs millions de personnes sont mal ou non inscrites sur les listes électorales et ne"
        "peuvent pas voter. Agissez pour changer cela.",
    ),
    (
        "accueil événements",
        "Accueillir de petits événements chez vous",
        "Organiser une soirée, un apéro, une écoute collective d'une émission télé...",
    ),
    (
        "participation événements",
        "Participer à des événements près de chez vous",
        "Être informé·e sur les événements organisés près de chez vous.",
    ),
    (
        "JRI",
        "Prendre des photos ou des vidéos près de chez vous",
        "Filmer ou photographier des événements locaux d'appui à la candidature.",
    ),
    (
        "appels",
        "Participer à la campagne d'appel",
        "Passer des appels téléphoniques depuis votre ordinateur.",
    ),
    (
        "facebook",
        "Agir sur Facebook",
        "Partager des publications, inviter vos ami·e·s, diffuser des informations...",
    ),
    (
        "twitter",
        "Agir sur Twitter",
        "Partager des tweets, partcipicer à des live-tweets d'émissions...",
    ),
    (
        "commentaires internet",
        "Commenter des articles sur internet",
        "Utiliser les espaces de commentaires sur les sites de presse, les blogs ou les forums...",
    ),
    (
        "vidéos musiques",
        "Proposer des vidéos et des musiques",
        "Réaliser des mini-reportages, zappings, chansons, fausses publicités, clips...",
    ),
    (
        "visuels",
        "Proposer des visuels et des dessins",
        "Réaliser des infographies, des mises en image de slogans, des caricatures...",
    ),
    (
        "blog",
        "Utiliser votre blog pour appuyer le mouvement",
        "Faire un lien vers lafranceinsoumise.fr, faire connaître nos idées...",
    ),
]


def add_basic_tags(apps, schema):
    PersonTag = apps.get_model("people", "PersonTag")

    for tag, description in info_tags:
        PersonTag.objects.update_or_create(
            label="info %s" % tag, defaults={"description": description}
        )

    for tag, short_description, long_description in agir_tags:
        description = "**%s**\n\n*%s*" % (short_description, long_description)
        PersonTag.objects.update_or_create(
            label="agir %s" % tag, defaults={"description": description}
        )


class Migration(migrations.Migration):
    dependencies = [("people", "0001_creer_modeles")]

    operations = [
        migrations.RunPython(add_basic_tags, reverse_code=migrations.RunPython.noop)
    ]
