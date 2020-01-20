import django_filters

from agir.groups.models import SupportGroupSubtype, SupportGroup
from agir.lib.filters import FixedModelMultipleChoiceFilter, DistanceFilter


class GroupFilterSet(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Chercher")

    subtypes = FixedModelMultipleChoiceFilter(
        field_name="subtypes",
        to_field_name="label",
        queryset=SupportGroupSubtype.objects.all(),
        label="Types de groupes",
    )

    distance = DistanceFilter(field_name="coordinates", label="Près de")

    def filter_search(self, qs, terms):
        if terms:
            return qs.search(terms)
        return qs

    class Meta:
        model = SupportGroup
        fields = ["search", "subtypes", "distance"]


class GroupAPIFilterSet(GroupFilterSet, django_filters.rest_framework.FilterSet):
    pass
