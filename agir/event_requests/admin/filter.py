from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter


class EventThemesAutocompleteFilter(AutocompleteRelatedModelFilter):
    title = "Thème"
    parameter_name = "theme"
    field_name = "event_theme"


class EventSpeakerAutocompleteFilter(AutocompleteRelatedModelFilter):
    title = "Intervenant·e"
    parameter_name = "speaker"
    field_name = "event_speaker"


class EventAutocompleteFilter(AutocompleteRelatedModelFilter):
    title = "Événement"
    parameter_name = "event"
    field_name = "event"
