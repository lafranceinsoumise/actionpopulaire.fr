from django import forms
from django.utils.translation import ugettext_lazy as _

from .geo import geocode_element
from .models import LocationMixin


class CoordinatesFormMixin(forms.Form):
    redo_geolocation = forms.BooleanField(label=_("Recalculer la position"), required=False, initial=False,
                                          help_text=_("Si cette case n'est pas cochée, la localisation n'est calculée"
                                                      " que si les coordonnées précédentes étaient automatiques et que"
                                                      " l'adresse a changé."))

    def save(self, commit=True):
        # on calcule la position si
        # - c'est demandé explicitement
        # - il n'y a pas de position pour cet item
        # - ou l'adresse a changé et ce n'était pas une position manuelle

        location_fields = ['location_name', 'location_address1', 'location_address2', 'location_city',
                           'location_zip',
                           'location_state', 'location_country']

        explicitly_asked_for = self.cleaned_data['redo_geolocation']
        no_location_yet = not self.instance.has_location()
        address_changed_with_automatic_location = (
            any(f in self.changed_data for f in location_fields) and self.instance.has_automatic_location()
        )
        should_geocode_now = explicitly_asked_for or no_location_yet or address_changed_with_automatic_location
        setting_manually = 'coordinates' in self.changed_data

        if should_geocode_now and not setting_manually:
            geocode_element(self.instance)

        if setting_manually:
            self.instance.coordinates_type = LocationMixin.COORDINATES_MANUAL

        return super().save(commit=commit)
