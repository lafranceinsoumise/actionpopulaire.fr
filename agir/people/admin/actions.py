from agir.people.actions.export import people_to_csv_response

ADMIN_PERSON_EXPORT_LIMIT = 500


def export_people_to_csv(modeladmin, request, queryset):
    return people_to_csv_response(queryset[:ADMIN_PERSON_EXPORT_LIMIT])


export_people_to_csv.short_description = f"Exporter les personnes en CSV (max. {ADMIN_PERSON_EXPORT_LIMIT} personnnes par export)"
export_people_to_csv.allowed_permissions = ["export"]
export_people_to_csv.select_across = True
export_people_to_csv.max_items = ADMIN_PERSON_EXPORT_LIMIT
