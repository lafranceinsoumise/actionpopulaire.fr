import json

import requests
from django import forms
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.template import loader
from django.utils.html import _json_script_escapes
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .geo import geocode_element
from .models import LocationMixin


class CoordinatesFormMixin(forms.Form):
    redo_geocoding = forms.BooleanField(
        label=_("Recalculer la position"),
        required=False,
        initial=False,
        help_text=_(
            "Si cette case n'est pas cochée, la localisation n'est calculée que si les coordonnées précédentes"
            " étaient automatiques et que l'adresse a changé. Cocher cette case ignorera tout changement de"
            " position éventuellement réalisé ci-dessus."
        ),
    )

    def save(self, commit=True, request=None):
        # on calcule la position si
        # - c'est demandé explicitement
        # - il n'y a pas de position pour cet item
        # - ou l'adresse a changé et ce n'était pas une position manuelle

        address_changed = any(
            f in self.changed_data for f in self.instance.GEOCODING_FIELDS
        )
        explicitly_asked_for = self.cleaned_data["redo_geocoding"]
        setting_manually = "coordinates" in self.changed_data

        if setting_manually and not explicitly_asked_for:
            self.instance.coordinates_type = LocationMixin.COORDINATES_MANUAL
        # if setting manually, we don't relocate

        if explicitly_asked_for or (
            address_changed and self.instance.should_relocate_when_address_changed()
        ):
            self.instance.location_citycode = ""
            # geocode directly in process
            try:
                geocode_element(self.instance)
            except (
                requests.HTTPError,
                requests.RequestException,
                requests.exceptions.Timeout,
            ):
                if request:
                    messages.warning(
                        request,
                        "La géolocalisation automatique n'est actuellement pas disponible. "
                        "Veuillez indiquer les coordonnées manuellement pour que l'élément apparaisse sur la carte.",
                    )

        return super().save(commit=commit)


class MediaInHead(forms.Media):
    def __repr__(self):
        return "MediaInHead(css=%r, js=%r)" % (self._css, self._js)

    def render(self):
        assets = {
            "js": [self.absolute_path(path) for path in self._js],
            "css": [
                [self.absolute_path(path), medium]
                for medium in self._css
                for path in self._css[medium]
            ],
        }

        json_assets = mark_safe(
            json.dumps(assets, cls=DjangoJSONEncoder).translate(_json_script_escapes)
        )

        return loader.get_template("lib/media_in_head.html").render(
            {"assets": json_assets}
        )

    def __add__(self, other):
        return MediaInHead.from_media(super().__add__(other))

    @classmethod
    def from_media(cls, media):
        return MediaInHead(js=media._js, css=media._css)
