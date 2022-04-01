from agir.groups.models import SupportGroup
from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter
from agir.lib.admin.form_fields import AutocompleteSelectModel
from agir.people.models import Person


class MonthlyAllocationSubscriptionPersonFilter(AutocompleteRelatedModelFilter):
    title = "Personne"
    parameter_name = "subscription_person"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.qs_filter_key = "subscription__person_id"

    def get_widget_instance(self):
        return AutocompleteSelectModel(
            Person,
            self.model_admin.admin_site,
        )

    def get_queryset_for_field(self):
        return Person.objects.all()


class MonthlyAllocationGroupFilter(AutocompleteRelatedModelFilter):
    title = "Groupe"
    parameter_name = "group"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.qs_filter_key = "group_id"

    def get_widget_instance(self):
        return AutocompleteSelectModel(
            SupportGroup,
            self.model_admin.admin_site,
        )

    def get_queryset_for_field(self):
        return SupportGroup.objects.all()
