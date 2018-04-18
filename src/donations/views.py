from django.views.generic import FormView, UpdateView, TemplateView
from django.urls import reverse_lazy

from people.models import Person
from payments.actions import get_payment_response
from payments.models import Payment

from . import forms


__all__ = ('AskAmountView', 'PersonalInformationView')


SESSION_DONATION_AMOUNT_KEY = '_donation_amount'


class AskAmountView(FormView):
    form_class = forms.DonationForm
    template_name = 'donations/ask_amount.html'
    success_url = reverse_lazy('donation_information')

    def form_valid(self, form):
        self.request.session[SESSION_DONATION_AMOUNT_KEY] = int(form.cleaned_data['amount']*100)
        return super().form_valid(form)


class PersonalInformationView(UpdateView):
    form_class = forms.DonatorForm
    template_name = 'donations/personal_information.html'

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user.person

        form = self.get_form()
        if 'email' in form.cleaned_data:
            try:
                return Person.objects.get_by_natural_key(form.cleaned_data['email'])
            except Person.DoesNotExist:
                pass

        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['amount'] = self.request.session[SESSION_DONATION_AMOUNT_KEY]
        return kwargs

    def form_valid(self, form):
        person = form.save()
        amount = form.cleaned_data['amount']

        return get_payment_response(
            person=person,
            type=Payment.TYPE_DONATION,
            price=amount,
            meta={'nationality': person.meta['nationality']}
        )


class ReturnView(TemplateView):
    template_name = 'donations/thanks.html'
