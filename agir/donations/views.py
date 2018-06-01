from django.views.generic import FormView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .apps import DonsConfig
from .tasks import send_donation_email
from ..people.models import Person
from ..payments.actions import create_and_get_payment_response
from ..payments.models import Payment

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

    def dispatch(self, request, *args, **kwargs):
        if SESSION_DONATION_AMOUNT_KEY not in request.session:
            return redirect('donation_amount')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user.person

        form = self.get_form()
        if form.is_valid():
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

        return create_and_get_payment_response(
            person=person,
            type=DonsConfig.PAYMENT_TYPE,
            price=amount,
            meta={'nationality': person.meta['nationality']}
        )


class ReturnView(TemplateView):
    template_name = 'donations/thanks.html'


def notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        send_donation_email.delay(payment.person.pk)
