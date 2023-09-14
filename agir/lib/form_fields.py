import json
from uuid import UUID

from data_france.models import Commune
from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
)
from django.forms.widgets import (
    Textarea,
    DateTimeBaseInput,
    Input,
    Select,
    SelectMultiple,
)
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django_countries import countries
from phonenumber_field.phonenumber import PhoneNumber

from agir.lib.iban import IBAN, to_iban
from agir.lib.time import dehumanize_naturaltime
from agir.lib.validators import (
    MinValueListValidator,
    MinDaysDeltaValidator,
    MaxDaysDeltaValidator,
    MaxValueListValidator,
)
from agir.lib.validators import validate_iban


class BootstrapDateTimePickerBaseWidget(DateTimeBaseInput):
    class Media:
        css = {
            "all": (
                "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/css/bootstrap-datetimepicker.min.css",
            )
        }
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.2/moment.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.2/locale/fr.js",
            "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/js/bootstrap-datetimepicker.min.js",
        )


class DateTimePickerWidget(BootstrapDateTimePickerBaseWidget):
    template_name = "custom_fields/date_time_picker.html"

    def format_value(self, value):
        return formats.localize_input(value, "%d/%m/%Y %H:%M")


class DatePickerWidget(BootstrapDateTimePickerBaseWidget):
    template_name = "custom_fields/date_picker.html"

    def format_value(self, value):
        return formats.localize_input(value, "%d/%m/%Y")


class RichEditorWidget(Textarea):
    template_name = "custom_fields/rich_editor.html"
    admin = False

    def __init__(self, attrs=None):
        default_attrs = {"class": "richeditorwidget"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["admin"] = self.admin
        return context


class AdminRichEditorWidget(RichEditorWidget):
    admin = True


class SelectizeMixin:
    template_name = "custom_fields/selectize_choice.html"
    create = False
    max_items = 1

    def __init__(self, *args, create=False, max_items=1, **kwargs):
        self.create = create
        self.max_items = max_items
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["max_items"] = self.max_items
        if self.create:
            context["widget"]["create"] = True
        return context

    class Media:
        css = {
            "all": (
                "https://cdnjs.cloudflare.com/ajax/libs/selectize.js/0.12.6/css/selectize.bootstrap3.min.css",
            )
        }
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/selectize.js/0.12.6/js/standalone/selectize.min.js",
        )


class RemoteSelectizeMixin(SelectizeMixin):
    template_name = "custom_fields/remote_selectize_choice.html"
    create = False

    def __init__(
        self,
        *args,
        api_url="",
        label_field="label",
        value_field="value",
        search_field="",
        sort_field="",
        base_query={},
        **kwargs,
    ):
        self.label_field = label_field
        self.value_field = value_field
        self.search_field = search_field
        self.sort_field = sort_field

        self.api_url = api_url + "?"
        self.api_url += "&".join(
            ["%s=%s" % (key, str(value)) for key, value in base_query.items()]
        )

        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context["widget"]["api_url"] = self.api_url
        context["widget"]["label_field"] = self.label_field
        context["widget"]["value_field"] = self.value_field
        context["widget"]["search_field"] = self.search_field
        context["widget"]["sort_field"] = self.sort_field

        return context


class SelectizeWidget(SelectizeMixin, Select):
    pass


class SelectizeMultipleWidget(SelectizeMixin, SelectMultiple):
    pass


class RemoteSelectizeWidget(RemoteSelectizeMixin, Select):
    pass


class AcceptCreativeCommonsLicenceField(forms.BooleanField):
    default_error_messages = {
        "required": _(
            "Vous devez accepter de placer votre image sous licence Creative Commons pour la téléverser"
        )
    }

    default_label = _(
        "En important une image, je certifie être le propriétaire des droits et accepte de la partager"
        ' sous licence libre <a href="https://creativecommons.org/licenses/by-nc-sa/3.0/fr/">Creative'
        " Commons CC-BY-NC 3.0</a>."
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("label", self.default_label)
        super().__init__(*args, **kwargs)


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, PhoneNumber):
            return o.as_e164
        if isinstance(o, IBAN):
            return o.as_stored_value
        return super().default(o)


class IBANWidget(Input):
    input_type = "text"
    template_name = "custom_fields/iban_widget.html"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs["data-component"] = "IBANField"
        super().__init__(attrs=attrs)


class IBANField(forms.Field):
    default_validators = [validate_iban]
    empty_value = ""
    default_error_messages = {
        "invalid": "Indiquez un numéro IBAN identifiant un compte existant. Ce numéro, composé de 14 à 34 chiffres et"
        " lettres, commence par deux lettres identifiant le pays du compte.",
        "forbidden_country": "Seuls les comptes des pays suivants sont autorisés : %(countries)s",
    }
    widget = IBANWidget

    def __init__(self, *args, allowed_countries=None, **kwargs):
        self.allowed_countries = allowed_countries
        super().__init__(*args, **kwargs)

        if self.allowed_countries is not None:
            # noinspection PyUnresolvedReferences
            self.widget.attrs["data-allowed-countries"] = ",".join(
                self.allowed_countries
            )
            # noinspection PyUnresolvedReferences
            self.widget.attrs[
                "data-allowed-countries-error"
            ] = self.allowed_countries_error_message()

    def to_python(self, value):
        if value in self.empty_values:
            return self.empty_value

        return to_iban(value)

    def allowed_countries_error_message(self):
        return self.error_messages["forbidden_country"] % {
            "countries": ", ".join(
                countries.name(code) or code for code in self.allowed_countries
            )
        }

    def validate(self, value):
        super().validate(value)

        is_empty = value == self.empty_value

        if not is_empty and not value.is_valid():
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        if (
            not is_empty
            and self.allowed_countries
            and value.country not in self.allowed_countries
        ):
            raise ValidationError(
                self.allowed_countries_error_message(), code="forbidden_country"
            )

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if not widget.is_hidden:
            attrs["minlength"] = 14
            attrs["maxlength"] = 34
        return attrs


class CommuneWidget(forms.Widget):
    template_name = "custom_fields/commune.html"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.setdefault("data-commune", "Y")
        super().__init__(attrs=attrs)

    def format_value(self, value):
        if value is None:
            return None

        return f"{value.type}-{value.code}"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value is not None:
            context["widget"]["label"] = f"{value.nom} ({value.code_departement})"

        return context


class CommuneField(forms.CharField):
    widget = CommuneWidget

    def __init__(self, *, types=None, **kwargs):
        self.types = types or []
        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        return {**super().widget_attrs(widget), "data-types": json.dumps(self.types)}

    def commune(self, value):
        try:
            if isinstance(value, int):
                return Commune.objects.get(pk=value)
            type, code = value.split("-")
            return Commune.objects.get(type=type, code=code)
        except (ValueError, Commune.DoesNotExist):
            raise ValidationError("Commune inconnue")

    def to_python(self, value):
        if value in self.empty_values:
            return None

        return self.commune(value)

    def prepare_value(self, value):
        if value == "" or value is None:
            return None

        if isinstance(value, Commune):
            return value

        try:
            return self.commune(value)
        except ValidationError:
            return None


class BetterIntegerInput(Input):
    """Widget à utiliser pour les champs de valeur entière.

    Ce widget doit être préféré au widget :class:`NumberInput` fourni par Django car celui-ci génère un
    élément input de type numeric qui est réputé peu accessible, et qui rajoute des éléments d'UI qui ne
    sont pas toujours appropriés (par exemple la modification du champ avec la molette de la souris, ou
    l'ajout de petites flèches pour modifier la valeur actuelle).

    Ce widget se contente de vérifier le format chiffre uniquement (potentiellement négatif), et indique
    aux navigateurs mobiles qu'un clavier numérique doit être affiché.
    """

    input_type = "text"
    template_name = "django/forms/widgets/input.html"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}

        attrs.setdefault("inputmode", "numeric")
        attrs.setdefault("pattern", "-?[0-9]+")
        attrs.setdefault("title", "Saisissez un nombre entier")
        super().__init__(attrs=attrs)


class MultiDateTimeBaseInput:
    template_name = "custom_fields/multi_date_widget.html"
    component = "MultiDateInput"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs["data-component"] = self.component
        attrs["data-format"] = self.widget_format
        super().__init__(attrs=attrs, format=self.format)

    def format_value(self, value):
        format_value = super().format_value
        if not value:
            return ""
        values = value
        if isinstance(value, str):
            values = set(value.strip().split(","))
        values = ",".join([formats.localize_input(v, self.format) for v in values if v])
        return values


class MultiDateTimeWidget(MultiDateTimeBaseInput, forms.DateTimeInput):
    widget_format = "YYYY-MM-DD HH:mm:ss"
    format = "%Y-%m-%dT%H:%M:%S%z"


class MultiDateWidget(MultiDateTimeBaseInput, forms.DateInput):
    widget_format = "YYYY-MM-DD"
    format = "%Y-%m-%d"


class MultiTemporaFieldMixin:
    empty_values = ("", [])
    default_error_messages = {
        "invalid": "Veuillez indiquer une ou plusieurs dates valides",
        "min_value": "Veuillez n'indiquer que des dates après le %(limit_value)s",
        "max_value": "Veuillez n'indiquer que des dates avant le %(limit_value)s",
        "min_length": ngettext_lazy(
            "Veuillez indiquer au moins une date",
            "Veuillez indiquer au moins %(limit_value)d dates",
            "limit_value",
        ),
        "max_length": ngettext_lazy(
            "Veuillez n'indiquer qu'une seule date",
            "Veuillez n'indiquer que %(limit_value)d dates maximum",
            "limit_value",
        ),
        "min_delta": ngettext_lazy(
            "La différence entre la première et la dernière date devrait être d'au moins un jour",
            "La différence entre la première et la dernière date devrait être d'au moins %(limit_value)d jours",
            "limit_value",
        ),
        "max_delta": ngettext_lazy(
            "La différence entre la première et la dernière date devrait être d'un jour maximum",
            "La différence entre la première et la dernière date devrait être de %(limit_value)d jours maximum",
            "limit_value",
        ),
    }

    def __init__(
        self,
        *args,
        min_value=None,
        max_value=None,
        min_length=None,
        max_length=None,
        min_delta=None,
        max_delta=None,
        validators=(),
        **kwargs,
    ):
        self.min_value = None
        if isinstance(min_value, str) and min_value:
            self.min_value = self.parse_date_string(min_value)
        self.max_value = None
        if isinstance(max_value, str) and max_value:
            self.max_value = self.parse_date_string(max_value)
        self.min_length = None
        if isinstance(min_length, int):
            self.min_length = max(0, min_length)
        self.max_length = None
        if isinstance(max_length, int):
            self.max_length = max(self.min_length or 0, 1, max_length)
        self.min_delta = None
        if isinstance(min_delta, int):
            self.min_delta = max(0, min_delta)
        self.max_delta = None
        if isinstance(max_delta, int):
            self.max_delta = max(self.min_delta or 0, 1, max_delta)

        validators = self.get_validators(validators)

        super().__init__(*args, validators=validators, **kwargs)

    def parse_date_string(self, string):
        try:
            date = timezone.datetime.strptime(string, "%Y-%m-%d")
        except ValueError:
            try:
                date = dehumanize_naturaltime(string)
            except ValueError:
                return None
        return date

    def get_validators(self, validators=()):
        if self.min_value is not None:
            validators += (MinValueListValidator(self.min_value),)
        if self.max_value is not None:
            validators += (MaxValueListValidator(self.max_value),)
        if self.min_length is not None:
            validators += (MinLengthValidator(self.min_length),)
        if self.max_length is not None:
            validators += (MaxLengthValidator(self.max_length),)
        if self.min_delta is not None:
            validators += (MinDaysDeltaValidator(self.min_delta),)
        if self.max_delta is not None:
            validators += (MaxDaysDeltaValidator(self.max_delta),)
        return validators

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.min_value is not None:
            attrs["min"] = self.min_value
        if self.max_value is not None:
            attrs["max"] = self.max_value
        if self.min_length is not None:
            attrs["data-min-length"] = self.min_length
        if self.max_length is not None:
            attrs["data-max-length"] = self.max_length
        if self.min_delta is not None:
            attrs["data-min-delta"] = self.min_delta
        if self.max_delta is not None:
            attrs["data-max-delta"] = self.max_delta
        return attrs

    def to_python(self, value):
        if value in self.empty_values:
            return []
        to_python = super().to_python
        values = value
        if isinstance(value, str):
            values = set(value.strip().split(","))
        return [to_python(v) for v in values if v]


class MultiDateField(MultiTemporaFieldMixin, forms.DateField):
    input_formats = ("%Y-%m-%d",)
    widget = MultiDateWidget

    def parse_date_string(self, string):
        datetime = super().parse_date_string(string)
        if datetime is None:
            return None
        return datetime.date()

    def __str__(self):
        return "MultiDateField"


class MultiDateTimeField(MultiTemporaFieldMixin, forms.DateTimeField):
    input_formats = ("%Y-%m-%dT%H:%M:%S%z",)
    widget = MultiDateTimeWidget

    def clean(self, value):
        return super().clean(value)

    def __str__(self):
        return "MultiDateTimeField"
