from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.forms import (
    Form,
    ModelMultipleChoiceField,
    ModelChoiceField,
    CheckboxSelectMultiple,
    RadioSelect,
)


class PollParticipationForm(Form):
    def __init__(self, *args, poll, **kwargs):
        super().__init__(*args, **kwargs)
        self.poll = poll
        self.helper = FormHelper()

        options = poll.options.all()
        if self.poll.rules.get("shuffle", True):
            options = options.order_by("?")

        if "options" in self.poll.rules and self.poll.rules["options"] == 1:
            self.fields["choice"] = ModelChoiceField(
                label="Choix",
                queryset=options,
                widget=RadioSelect,
                required=True,
                empty_label=None,
                initial=None,
            )
        else:
            self.fields["choice"] = ModelMultipleChoiceField(
                label="Choix",
                queryset=options,
                widget=CheckboxSelectMultiple(),
            )

        self.helper.add_input(Submit("submit", "Confirmer"))

    def clean_choice(self):
        if "options" in self.poll.rules and self.poll.rules["options"] == 1:
            return [self.cleaned_data["choice"]]
        else:
            if self.cleaned_data["choice"].count() == 0:
                raise ValidationError("Vous n'avez pas sélectionné d'options")
            if (
                "options" in self.poll.rules
                and self.cleaned_data["choice"].count() != self.poll.rules["options"]
            ):
                raise ValidationError(
                    "Vouns devez sélectionner % options" % self.poll.rules["options"]
                )
            if (
                "min_options" in self.poll.rules
                and self.cleaned_data["choice"].count() < self.poll.rules["min_options"]
            ):
                raise ValidationError(
                    "Vous devez sélectionner au minimum %d options"
                    % self.poll.rules["min_options"]
                )
            if (
                "max_options" in self.poll.rules
                and self.cleaned_data["choice"].count() > self.poll.rules["max_options"]
            ):
                raise ValidationError(
                    "Vous devez sélectionner au maximum %d options"
                    % self.poll.rules["max_options"]
                )
            return self.cleaned_data["choice"]

    def make_choice(self, user):
        choice = self.cleaned_data["choice"]
        self.poll_choice = self.poll.make_choice(user.person, choice)
        return self.poll_choice
