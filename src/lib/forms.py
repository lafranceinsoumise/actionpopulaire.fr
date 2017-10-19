from django import forms
from django.utils.translation import ugettext_lazy as _

from .geo import geocode_element
from .models import LocationMixin


class CoordinatesFormMixin(forms.Form):
    redo_geocoding = forms.BooleanField(
        label=_("Recalculer la position"), required=False, initial=False,
        help_text=_("Si cette case n'est pas cochée, la localisation n'est calculée que si les coordonnées précédentes"
                    " étaient automatiques et que l'adresse a changé. Cocher cette case ignorera tout changement de"
                    " position éventuellement réalisé ci-dessus."))

    def save(self, commit=True):
        # on calcule la position si
        # - c'est demandé explicitement
        # - il n'y a pas de position pour cet item
        # - ou l'adresse a changé et ce n'était pas une position manuelle

        address_changed = any(f in self.changed_data for f in self.instance.GEOCODING_FIELDS)
        explicitly_asked_for = self.cleaned_data['redo_geocoding']
        setting_manually = 'coordinates' in self.changed_data

        if setting_manually and not explicitly_asked_for:
            self.instance.coordinates_type = LocationMixin.COORDINATES_MANUAL
        # if setting manually, we don't relocate

        if explicitly_asked_for or (address_changed and self.instance.should_relocate_when_address_changed()):
            # geocode directly in process
            geocode_element(self.instance)

        return super().save(commit=commit)
