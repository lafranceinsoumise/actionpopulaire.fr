from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter


class TagListFilter(AutocompleteRelatedModelFilter):
    field_name = "tags"
    title = "Tag"


class ExcludedTagListFilter(AutocompleteRelatedModelFilter):
    field_name = "excluded_tags"
    title = "Tag à exclure"


class QualificationListFilter(AutocompleteRelatedModelFilter):
    field_name = "qualifications"
    title = "Statut"


class SupportGroupSubtypeListFilter(AutocompleteRelatedModelFilter):
    field_name = "supportgroup_subtypes"
    title = "Sous-type de groupe"
