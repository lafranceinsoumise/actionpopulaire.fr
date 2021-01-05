from django.db import migrations


def create_basic_subtypes(apps, schema_editor):
    SupportGroupSubtype = apps.get_model("groups", "SupportGroupSubtype")
    SupportGroup = apps.get_model("groups", "SupportGroup")
    subtypes = {
        "groupe local": {
            "description": "Sous-groupe par défaut de tous les groupes locaux",
            "hide_text_label": True,
            "visibility": "A",
            "color": "#0098b6",
            "type": "L",  # local
        },
        "rédaction du livret": {
            "description": "Groupe de rédaction du livret.",
            "visibility": "D",
            "type": "B",  # thématique
        },
        "équipe de soutien": {
            "description": "Sous-type par défaut des équipes de soutien",
            "hide_text_label": True,
            "visibility": "A",  # all
            "color": "#571aff",
            "type": "2",  # campagne 2022
        },
    }
    for label, options in subtypes.items():
        SupportGroupSubtype.objects.update_or_create(label=label, defaults=options)


class Migration(migrations.Migration):
    dependencies = [("groups", "0001_creer_modeles")]

    operations = [
        migrations.RunPython(
            code=create_basic_subtypes, reverse_code=migrations.RunPython.noop
        )
    ]
