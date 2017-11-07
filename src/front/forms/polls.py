from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.forms import Form, ModelMultipleChoiceField, CheckboxSelectMultiple


class PollParticipationForm(Form):
    def __init__(self, *args, poll, **kwargs):
        super().__init__(*args, **kwargs)
        self.poll = poll
        self.helper = FormHelper()
        self.fields['choice'] = ModelMultipleChoiceField(
            label='Choix',
            queryset=poll.options.all(),
            widget=CheckboxSelectMultiple(),
        )
        self.helper.add_input(Submit('submit', 'Confirmer'))

    def clean_choice(self):
        if self.cleaned_data['choice'].count() == 0:
            raise ValidationError("Vous n'avez pas sélectionné d'options")
        if self.cleaned_data['choice'].count() < self.poll.rules['min_options']:
            raise ValidationError('Vous devez sélectionner au minimum %d options' % self.poll.rules['min_options'])
        if self.cleaned_data['choice'].count() > self.poll.rules['max_options']:
            raise ValidationError('Vous devez sélectionner au maximum %d options' % self.poll.rules['min_options'])

        return self.cleaned_data['choice']

    def make_choice(self, user):
        choice = self.cleaned_data['choice']
        self.poll.make_choice(user.person, choice)




