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
from django.utils.translation import ngettext

OVERRIDABLE_POLL_RULE_KEYS = ["options", "min_options", "max_options", "shuffle"]


class PollParticipationForm(Form):
    def __init__(self, *args, poll, **kwargs):
        super().__init__(*args, **kwargs)
        self.poll = poll
        self.helper = FormHelper()

        for option_group_id, options in self.get_option_groups().items():
            self.add_field(options, option_group_id)

        self.helper.add_input(Submit("submit", "Confirmer"))

    def get_option_groups(self):
        option_groups = {
            key: self.poll.options.filter(option_group_id=key)
            for key in self.poll.options.values_list(
                "option_group_id", flat=True
            ).distinct()
        }

        return option_groups

    def get_poll_rules_for_option_group(self, option_group_id):
        rules = self.poll.rules

        if "option_groups" in rules and option_group_id in rules["option_groups"]:
            rules = {**rules["option_groups"][option_group_id]}
            rules.update(
                {
                    key: default_value
                    for key, default_value in self.poll.rules.items()
                    if key in OVERRIDABLE_POLL_RULE_KEYS and key not in rules
                }
            )

        return rules

    def add_field(self, options, option_group_id):
        rules = self.get_poll_rules_for_option_group(option_group_id)
        label = rules.get("label", "Choix")

        if rules.get("shuffle", True):
            options = options.order_by("?")

        if "options" in rules and rules["options"] == 1:
            self.fields[option_group_id] = ModelChoiceField(
                label=label,
                queryset=options,
                widget=RadioSelect,
                required=True,
                empty_label=None,
                initial=None,
            )
            return

        help_text = ""
        if rules.get("help_text", None):
            help_text = rules["help_text"]
        elif rules.get("options", None):
            help_text = (
                f"Vous devez sélectionner exactement {rules['options']} options."
            )
        elif rules.get("min_options", None) and rules.get("max_options", None):
            help_text = f"Vous pouvez sélectionner entre {rules['min_options']} et {rules['max_options']} options."
        elif rules.get("min_options", None):
            help_text = ngettext(
                f"Vous devez sélectionner au moins une option.",
                f"Vous devez sélectionner au moins {rules['min_options']} options.",
                rules["min_options"],
            )
        elif rules.get("max_options", None):
            help_text = ngettext(
                f"Vous pouvez sélectionner au maximum une option.",
                f"Vous pouvez sélectionner jusqu'à {rules['max_options']} options.",
                rules["max_options"],
            )

        self.fields[option_group_id] = ModelMultipleChoiceField(
            label=label,
            queryset=options,
            widget=CheckboxSelectMultiple(),
            help_text=help_text,
        )

    def _clean_choice(self, option_group_id, cleaned_data):
        rules = self.get_poll_rules_for_option_group(option_group_id)

        if "options" in rules and rules["options"] == 1:
            return [cleaned_data.pk]

        if not cleaned_data or cleaned_data.count() == 0:
            raise ValidationError("Vous n'avez pas sélectionné d'options")

        cleaned_data = list(set(cleaned_data.values_list("pk", flat=True)))

        if rules.get("options", None) and len(cleaned_data) != rules["options"]:
            raise ValidationError(
                ngettext(
                    "Veuillez sélectionner exactement une option.",
                    f"Veuillez sélectionner exactement {rules['options']} options.",
                    rules["options"],
                )
            )

        if rules.get("min_options", None) and len(cleaned_data) < rules["min_options"]:
            raise ValidationError(
                ngettext(
                    "Veuillez sélectionner au moins une option.",
                    f"Veuillez sélectionner minimum {rules['min_options']} options.",
                    rules["min_options"],
                )
            )

        if rules.get("max_options", None) and len(cleaned_data) > rules["max_options"]:
            raise ValidationError(
                ngettext(
                    "Veuillez sélectionner au maximum une option.",
                    f"Veuillez sélectionner au maximum {rules['max_options']} options.",
                    rules["max_options"],
                )
            )

        return cleaned_data

    def clean(self):
        option_groups = self.get_option_groups()
        selection = {key: self.cleaned_data.get(key, []) for key in option_groups}

        for option_group_id, cleaned_data in selection.items():
            try:
                selection[option_group_id] = self._clean_choice(
                    option_group_id, cleaned_data
                )
            except ValidationError as e:
                self.add_error(option_group_id, error=e)

        return {**self.cleaned_data, "selection": selection}

    def make_choice(self, user):
        selection = self.cleaned_data["selection"]
        self.poll_choice = self.poll.make_choice(user.person, selection)
        return self.poll_choice
