from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.widgets import Textarea, DateTimeBaseInput, Input, Select
from django.utils import formats
from django.utils.translation import ugettext_lazy as _
from django_countries import countries
from phonenumber_field.phonenumber import PhoneNumber
from webpack_loader import utils as webpack_loader_utils
from webpack_loader.utils import get_files

from agir.donations.validators import validate_iban
from agir.lib.iban import IBAN, to_iban


class DateTimePickerWidget(DateTimeBaseInput):
    template_name = "custom_fields/date_time_picker.html"

    def format_value(self, value):
        return formats.localize_input(value, "%d/%m/%Y %H:%M")

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

    @property
    def media(self):
        return forms.Media(
            js=(webpack_loader_utils.get_files("front/richEditor")[0]["url"],)
        )


class AdminRichEditorWidget(RichEditorWidget):
    admin = True


class AdminJsonWidget(Textarea):
    admin = True
    template_name = "custom_fields/admin_json.html"
    schema = None

    def __init__(self, schema=None, attrs=None):
        self.schema = schema
        default_attrs = {"class": "jsoneditor"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["widget"]["schema"] = self.schema
        return context

    @property
    def media(self):
        return forms.Media(
            js=(webpack_loader_utils.get_files("lib/adminJsonWidget")[0]["url"],)
        )


class SelectizeWidget(Select):
    template_name = "custom_fields/selectize_choice.html"
    create = False

    def __init__(self, *args, create=False, **kwargs):
        self.create = create
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
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
        if isinstance(o, PhoneNumber):
            return o.as_e164
        if isinstance(o, IBAN):
            return o.as_stored_value
        return super().default(o)


class IBANWidget(Input):
    input_type = "text"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs["data-component"] = "IBANField"
        super().__init__(attrs=attrs)

    @property
    def media(self):
        return forms.Media(
            js=[script["url"] for script in get_files("lib/IBANField", "js")]
        )


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
        if value != self.empty_value and not value.is_valid():
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        if self.allowed_countries and value.country not in self.allowed_countries:
            raise ValidationError(
                self.allowed_countries_error_message(), code="forbidden_country"
            )

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if not widget.is_hidden:
            attrs["minlength"] = 14
            attrs["maxlength"] = 34
        return attrs
