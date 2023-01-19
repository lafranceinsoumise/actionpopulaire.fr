from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter


class EventThemesAutocompleteFilter(AutocompleteRelatedModelFilter):
    title = "Thème"
    parameter_name = "theme"
