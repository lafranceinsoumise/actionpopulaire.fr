from .models import LocationModel
from ..serializers import LegacyLocationMixin


class LocationSerializer(LegacyLocationMixin):
    class Meta:
        model = LocationModel
        fields = ("location",)
