from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, HTML, Fieldset
from django import forms
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from agir.lib.form_components import HalfCol, FullCol
from agir.lib.form_mixins import TagMixin
from agir.people.form_mixins import ContactPhoneNumberMixin
from agir.people.models import PersonTag, Person
from agir.people.tags import action_tags


class VolunteerForm(ContactPhoneNumberMixin, TagMixin, forms.ModelForm):
    tags = [
        (
            tag,
            format_html(
                "<strong>{}</strong><br><small><em>{}</em></small>", title, description
            ),
        )
        for _, tags in action_tags.items()
        for tag, title, description in tags
    ]
    tag_model_class = PersonTag

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", _("M'enregistrer comme volontaire")))

        self.helper.layout = Layout(
            Row(
                FullCol(
                    Fieldset(
                        "Vie du mouvement",
                        Row(HalfCol("draw_participation"), HalfCol("gender")),
                    )
                ),
                HalfCol(
                    Fieldset(
                        "Agir près de chez vous",
                        *(tag for tag, title, desc in action_tags["nearby"])
                    )
                ),
                HalfCol(
                    Fieldset(
                        "Agir sur internet",
                        *(tag for tag, title, desc in action_tags["internet"])
                    )
                ),
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["draw_participation"] and not cleaned_data["gender"]:
            self.add_error(
                "gender",
                forms.ValidationError(
                    _(
                        "Votre genre est obligatoire pour pouvoir organiser un tirage au sort paritaire"
                    )
                ),
            )

        return cleaned_data

    class Meta:
        model = Person
        fields = ("draw_participation", "gender")
