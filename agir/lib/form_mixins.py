import json
import re
import string
from collections import Counter
from pathlib import PurePath
from typing import List, Mapping, Optional
from uuid import uuid4

import iso8601
import os

import requests
from crispy_forms.layout import Submit, Row
from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import RegexValidator
from django.db import IntegrityError
from django.forms import fields_for_model
from django.template import loader
from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext_lazy as _, gettext
from django.utils.html import format_html, _json_script_escapes
from django.contrib.gis.forms.widgets import OSMWidget
from crispy_forms.helper import FormHelper
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import NumberParseException
from unidecode import unidecode

from agir.lib.form_components import *
from agir.lib.form_fields import AcceptCreativeCommonsLicenceField
from agir.lib.geo import geocode_element
from agir.lib.models import LocationMixin

from django.utils.translation import gettext as _
from django_countries import countries

__all__ = [
    "TagMixin",
    "LocationFormMixin",
    "ContactFormMixin",
    "MetaFieldsMixin",
    "LocationMixin",
    "MediaInHead",
    "CoordinatesFormMixin",
]

french_zipcode_validator = RegexValidator(
    r"[0-9]{5}", message="Un code postal valide est obligatoire."
)


class TagMixin:
    tags = []
    tag_model_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        active_tags = [
            tag.label
            for tag in self.instance.tags.filter(
                label__in=[tag for tag, tag_label in self.tags]
            )
        ]

        for tag, tag_label in self.tags:
            self.fields[tag] = forms.BooleanField(
                label=tag_label, required=False, initial=tag in active_tags
            )

    def _save_m2m(self):
        """save all tags
        :return:
        """
        super()._save_m2m()

        tags = list(
            self.tag_model_class.objects.filter(label__in=[tag for tag, _ in self.tags])
        )
        tags_to_create = [
            self.tag_model_class(label=tag_label)
            for tag_label, _ in self.tags
            if tag_label not in {tag.label for tag in tags}
        ]

        if tags_to_create:
            # PostgreSQL only will set the id on original objects
            self.tag_model_class.objects.bulk_create(tags_to_create)

        tags += tags_to_create

        tags_in = set(
            tag
            for tag in tags
            if tag.label in self.cleaned_data and self.cleaned_data[tag.label]
        )
        tags_out = set(
            tag
            for tag in tags
            if tag.label in self.cleaned_data and not self.cleaned_data[tag.label]
        )

        current_tags = set(self.instance.tags.all())

        # all tags that have to be added
        tags_missing = tags_in - current_tags
        if tags_missing:
            try:
                self.instance.tags.add(*tags_missing)
            except IntegrityError:
                pass

        tags_excess = tags_out & current_tags
        if tags_excess:
            self.instance.tags.remove(*tags_excess)


class LocationFormMixin:
    geocoding_task = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in ["location_address1", "location_city", "location_country"]:
            if f in self.fields:
                self.fields[f].required = True

        self.fields["location_country"].choices = countries

        self.fields["location_address1"].label = _("Adresse")
        self.fields["location_address2"].label = False

        if not hasattr(self, "location_country") or not self.instance.location_country:
            self.fields["location_country"].initial = "FR"

    def clean(self):
        """Makes zip code compulsory for French address"""
        cleaned_data = super().clean()

        if cleaned_data.get("location_country") == "FR":
            try:
                french_zipcode_validator(cleaned_data.get("location_zip"))
            except ValidationError as e:
                self.add_error("location_zip", e)

        return cleaned_data

    def must_geolocate(self):
        address_changed = any(
            f in LocationMixin.GEOCODING_FIELDS for f in self.changed_data
        )
        return address_changed and self.instance.should_relocate_when_address_changed()

    def save(self, commit=True):
        # reset address if we must geolocate again
        if self.must_geolocate():
            self.instance.coordinates = None
            self.instance.coordinates_type = None

        return super().save(commit=True)

    def schedule_tasks(self):
        if self.must_geolocate():
            self.geocoding_task.delay(self.instance.pk)


LocationFormMixin.declared_fields = fields_for_model(
    LocationMixin,
    fields=[
        "location_name",
        "location_address1",
        "location_address2",
        "location_city",
        "location_zip",
        "location_country",
    ],
)


class ContactFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["contact_email"].required = True
        self.fields["contact_phone"].required = True


class GeocodingBaseForm(forms.ModelForm):
    geocoding_task = None
    messages = {"use_geocoding": None, "coordinates_updated": None}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["coordinates"].widget = OSMWidget()

        self.helper = FormHelper()
        self.helper.form_method = "POST"

        form_elements = []

        form_elements += [
            Row(FullCol(Div("coordinates"))),
            Row(
                FullCol(
                    HTML(
                        format_html(
                            gettext(
                                "<strong>Type de coordonnées actuelles</strong> : {}"
                            ),
                            self.instance.get_coordinates_type_display(),
                        )
                    )
                )
            ),
        ]

        if self.instance.has_manual_location():
            self.fields["use_geocoding"] = forms.BooleanField(
                required=False,
                label="Revenir à la localisation automatique à partir de l'adresse",
                help_text=_(
                    "Cochez cette case pour annuler la localisation manuelle de votre groupe d'action."
                ),
            )
            form_elements.append(Row(FullCol("use_geocoding")))

        form_elements.append(
            Row(
                ThirdCol(
                    Submit(
                        "submit", "Sauvegarder", css_class="btn btn-default btn-block"
                    ),
                    css_class="padtopmore",
                )
            )
        )
        self.helper.layout = Layout(*form_elements)

    def save(self, commit=True):
        if self.cleaned_data.get("use_geocoding"):
            self.instance.coordinates_type = None
            self.instance.coordinates = None
            super().save(commit=commit)
            self.geocoding_task.delay(self.instance.pk)
        else:
            if "coordinates" in self.changed_data:
                self.instance.coordinates_type = self.instance.COORDINATES_MANUAL
                super().save(commit=commit)

        return self.instance

    def get_message(self):
        if self.cleaned_data.get("use_geocoding"):
            return self.messages["use_geocoding"]
        elif "coordinates" in self.changed_data:
            return self.messages["coordinates_updated"]

        return None


class SearchByZipCodeFormBase(forms.Form):
    lon = forms.FloatField(widget=forms.HiddenInput())
    lat = forms.FloatField(widget=forms.HiddenInput())
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _(
                    "Indiquez une autre adresse autour de laquelle rechercher"
                ),
                "class": "form-control",
            }
        ),
    )


class MetaFieldsMixin:
    meta_fields = []
    meta_attr = "meta"
    meta_prefix = ""
    filepath = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_meta_initial(check_field_type=False)

    def update_meta_initial(self, check_field_type=True):
        for f in self.get_meta_fields():
            stored_value = getattr(self.instance, self.meta_attr).get(
                self.meta_prefix + f
            )
            if (
                check_field_type
                and isinstance(self.fields[f], forms.FileField)
                and stored_value
            ):
                path = stored_value
                stored_value = default_storage.open(path)
                stored_value.name = os.path.basename(path)
                stored_value.url = settings.MEDIA_URL + path
            self.initial[f] = stored_value

    def get_formatted_value(self, field_name, value, html=False):
        if field_name not in self.fields:
            return value

        if value is None:
            return "NA"

        field = self.fields[field_name]

        if isinstance(field, forms.DateTimeField):
            date = iso8601.parse_date(value)
            return localize(date.astimezone(get_current_timezone()))
        elif isinstance(field, PhoneNumberField):
            try:
                phone_number = PhoneNumber.from_string(value)
                return phone_number.as_international
            except NumberParseException:
                return value
        elif isinstance(field, forms.FileField):
            url = settings.FRONT_DOMAIN + settings.MEDIA_URL + value
            if html:
                return format_html('<a href="{}">Accéder au fichier</a>', url)
            else:
                return url

        return value

    def get_meta_fields(self):
        return self.meta_fields

    def _post_clean(self):
        super()._post_clean()

        meta_update = {
            self.meta_prefix + f: self.cleaned_data.get(f, "")
            for f in self.get_meta_fields()
            if self.cleaned_data.get(f) is not None
        }
        getattr(self.instance, self.meta_attr).update(meta_update)

    def _save_files(self):
        for key, value in self.cleaned_data.items():
            if isinstance(value, File):
                extension = os.path.splitext(value.name)[1].lower()
                path = str(PurePath(self.filepath) / (str(uuid4()) + extension))
                default_storage.save(path, value)
                getattr(self.instance, self.meta_attr)[self.meta_prefix + key] = path


class ImageFormMixin(forms.Form):
    image_field = None
    image_accept_license = AcceptCreativeCommonsLicenceField()

    def clean(self):
        cleaned_data = super().clean()
        report_image = cleaned_data.get(self.image_field, None)
        accept_license = cleaned_data.get("image_accept_license", False)

        if (
            report_image
            and self.image_field in self.changed_data
            and not accept_license
        ):
            self.add_error(
                "image_accept_license",
                self.fields["image_accept_license"].error_messages["required"],
            )

        return cleaned_data


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


class ImportTableForm(forms.Form):
    columns_namespace = "COL_"
    columns_key = "columns"
    dest_columns = None
    PUNCTUATION_RE = re.compile(rf"[{re.escape(string.punctuation)}]+")
    MULTIPLE_WHITESPACE_RE = re.compile(r"\s+")

    def __init__(
        self,
        *args,
        source_file_columns: List[str],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.source_file_columns = source_file_columns

        defaults = {self.normalize_col_name(v): k for k, v in self.dest_columns.items()}
        empty_choice = ("", "Ne pas utiliser")
        choices = (empty_choice, *(self.dest_columns.items()))

        fields = {
            f"{self.columns_namespace}{i}": forms.ChoiceField(
                choices=choices,
                required=False,
                default=defaults.get(self.normalize_col_name(col), ""),
            )
            for i, col in enumerate(source_file_columns)
        }

        self.fields.update(fields)

    def clean_columns(self, columns: List[Optional[str]]) -> List[Optional[str]]:
        # par défaut, on vérifie simplement qu'aucune valeur de colonne n'a été sélectionnée plus d'une fois
        c = Counter(columns)
        if c.most_common(n=1)[0][1] > 1:
            raise forms.ValidationError(
                "Vous ne pouvez sélectionner qu'au plus une fois chaque champ."
            )

        return columns

    def clean(self):
        cleaned_data = super().clean()

        # on renvoie une liste plutôt qu'un dictionnaire parce qu'on a pas de garantie que
        # les colonnes du fichier source soient uniques
        columns = [
            cleaned_data.get(f"{self.columns_namespace}{i}", None)
            for i in range(len(self.source_file_columns))
        ]

        columns = self.clean_columns(columns)

        cleaned_data[self.columns_key] = columns

        return cleaned_data

    @classmethod
    def normalize_col_name(cls, col):
        col = unidecode(col)
        col = cls.PUNCTUATION_RE.sub(" ", col)
        col = cls.MULTIPLE_WHITESPACE_RE.sub(" ", col)

        return col.lower().strip()
