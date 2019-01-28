from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Field, HTML
from django import forms
from django.utils.translation import ugettext_lazy as _

from agir.lib.form_components import HalfCol, FullCol
from agir.lib.form_mixins import TagMixin, MetaFieldsMixin
from agir.lib.models import RE_FRENCH_ZIPCODE
from agir.lib.tasks import geocode_person
from agir.people.form_mixins import ContactPhoneNumberMixin
from agir.people.models import PersonTag, Person
from agir.people.tags import skills_tags


class ProfileForm(MetaFieldsMixin, ContactPhoneNumberMixin, TagMixin, forms.ModelForm):
    tags = skills_tags
    tag_model_class = PersonTag
    meta_fields = [
        "occupation",
        "associations",
        "unions",
        "party",
        "party_responsibility",
        "other",
    ]

    occupation = forms.CharField(max_length=200, label=_("Métier"), required=False)
    associations = forms.CharField(
        max_length=200, label=_("Engagements associatifs"), required=False
    )
    unions = forms.CharField(
        max_length=200, label=_("Engagements syndicaux"), required=False
    )
    party = forms.CharField(max_length=60, label=_("Parti politique"), required=False)
    party_responsibility = forms.CharField(max_length=100, label=False, required=False)
    other = forms.CharField(
        max_length=200, label=_("Autres engagements"), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Enregistrer mes informations"))

        self.fields["location_address1"].label = _("Adresse")
        self.fields["location_address2"].label = False
        self.fields["location_country"].required = True

        self.helper.layout = Layout(
            Row(
                HalfCol(  # contact part
                    Row(HalfCol("first_name"), HalfCol("last_name")),
                    Row(
                        HalfCol("gender"),
                        HalfCol(Field("date_of_birth", placeholder=_("JJ/MM/AAAA"))),
                    ),
                    Row(
                        FullCol(
                            Field("location_address1", placeholder=_("1ère ligne")),
                            Field("location_address2", placeholder=_("2ème ligne")),
                        )
                    ),
                    Row(HalfCol("location_zip"), HalfCol("location_city")),
                    Row(FullCol("location_country")),
                    Row(HalfCol("contact_phone"), HalfCol("occupation")),
                    Row(HalfCol("associations"), HalfCol("unions")),
                    Row(
                        HalfCol(
                            Field("party", placeholder="Nom du parti"),
                            Field("party_responsibility", placeholder="Responsabilité"),
                        ),
                        HalfCol("other"),
                    ),
                    Row(FullCol(Field("mandates"))),
                ),
                HalfCol(
                    HTML("<label>Savoir-faire</label>"),
                    *(tag for tag, desc in skills_tags)
                ),
            )
        )

    def clean(self):
        if self.cleaned_data.get("location_country") == "FR":
            if self.cleaned_data["location_zip"] == "":
                self.add_error(
                    "location_zip",
                    forms.ValidationError(
                        self.fields["location_zip"].error_messages["required"],
                        code="required",
                    ),
                )
            elif not RE_FRENCH_ZIPCODE.match(self.cleaned_data["location_zip"]):
                self.add_error(
                    "location_zip",
                    forms.ValidationError(
                        _("Merci d'indiquer un code postal valide"), code="invalid"
                    ),
                )

        return self.cleaned_data

    def _save_m2m(self):
        super()._save_m2m()

        address_has_changed = any(
            f in self.changed_data for f in self.instance.GEOCODING_FIELDS
        )

        if address_has_changed and self.instance.should_relocate_when_address_changed():
            geocode_person.delay(self.instance.pk)

    class Meta:
        model = Person
        fields = (
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "location_address1",
            "location_address2",
            "location_city",
            "location_zip",
            "location_country",
            "contact_phone",
            "mandates",
        )
