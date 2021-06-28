from django.db import migrations

CREATE_SEARCH_INDEX = """
-- noinspection SqlResolve
CREATE INDEX events_event_search ON events_event USING GIN ((
setweight(to_tsvector('french_unaccented', COALESCE("name", '')), 'A')
|| setweight(to_tsvector('french_unaccented', COALESCE("location_name", '')), 'B')
|| setweight(to_tsvector('french_unaccented', COALESCE("location_city", '')), 'B')
|| setweight(to_tsvector('french_unaccented', COALESCE("location_zip", '')), 'B')
|| setweight(to_tsvector('french_unaccented', COALESCE("description", '')), 'C')
|| setweight(to_tsvector('french_unaccented', COALESCE("report_content", '')), 'C')
));
"""
DELETE_SEARCH_INDEX = """
-- noinspection SqlResolve
DROP INDEX events_event_search RESTRICT;
"""


def create_default_subtypes(apps, schema):
    EventSubtype = apps.get_model("events", "EventSubtype")

    subtypes = {
        "autre reunion groupe": {
            "description": "Autre type de réunion de groupe",
            "hide_text_label": True,
            "color": "#00B400",
            "type": "G",
            "visibility": "A",
        },
        "autre reunion publique": {
            "description": "Autre type de réunion publique",
            "hide_text_label": True,
            "color": "#0098B6",
            "type": "M",
            "visibility": "A",
        },
        "autre action publique": {
            "description": "Autre type d'action publique",
            "hide_text_label": True,
            "color": "#C9462C",
            "type": "A",
            "visibility": "A",
        },
        "autre evenement": {
            "description": "Tout autre type d'événement",
            "hide_text_label": True,
            "type": "O",
            "visibility": "A",
        },
    }

    for label, options in subtypes.items():
        EventSubtype.objects.update_or_create(label=label, defaults=options)


class Migration(migrations.Migration):
    dependencies = [("events", "0001_creer_modeles")]

    operations = [
        migrations.RunSQL(sql=CREATE_SEARCH_INDEX, reverse_sql=DELETE_SEARCH_INDEX),
        migrations.RunPython(
            code=create_default_subtypes, reverse_code=migrations.RunPython.noop
        ),
    ]
