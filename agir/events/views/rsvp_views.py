from django.urls import reverse
from django.db import transaction
from django.db.models import F, Sum
from django.views.generic import UpdateView, DetailView, RedirectView
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseBadRequest

from ..apps import EventsConfig
from ..models import Event, RSVP
from ..tasks import send_rsvp_notification
from agir.people.models import PersonFormSubmission
from agir.payments.actions import create_and_get_payment_response
from agir.payments.models import Payment

from ..forms import (BillingForm, GuestsForm)
from agir.front.view_mixins import HardLoginRequiredMixin


class RSVPEventView(HardLoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/rsvp_event.html'

    def get_form(self):
        if self.object.subscription_form is None:
            return None

        form_class = self.object.subscription_form.get_form()

        kwargs = {'instance': self.request.user.person}

        if self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.request.POST

        is_guest = RSVP.objects.filter(event=self.object, person=self.request.user.person, canceled=False).first() is not None

        return form_class(empty=is_guest, **kwargs)

    def get_context_data(self, **kwargs):
        rsvp = self.request.user.is_authenticated and self.object.rsvps.filter(
                person=self.request.user.person).first()
        form = self.get_form()

        return super().get_context_data(
            form=form,
            event=self.object,
            rsvp=rsvp,
            submission_data={
                form.fields[id].label: value
                for id, value in rsvp.form_submission.data.items()
            } if rsvp and rsvp.form_submission else None,
            guests_submission_data=[{
                form.fields[id].label: value
                for id, value in form_submission.data.items()
            } for form_submission in rsvp.guests_form_submissions.all()] if rsvp else None,
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.subscription_form is None:
            return HttpResponseRedirect(reverse('view_event', args=[self.object.pk]))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        submission = None
        guests = 0

        if self.object.allow_guests:
            guests_form = GuestsForm(self.request.POST)
            if guests_form.is_valid():
                guests = guests_form.cleaned_data['guests']

        if self.object.subscription_form is not None:
            form = self.get_form()

            if form.is_valid():
                # we save the submission date but we delay saving the person itself unit we know if this
                # is the person submission or a guest submission
                unsaved_person = form.save(commit=False)
                form.save_m2m()
                submission = form.submission
            else:
                context = self.get_context_data(object=self.object)
                return self.render_to_response(context)

        if self.object.payment_parameters is None:
            # Does not prevent race conditions and ending with more participants than maximum
            with transaction.atomic():
                sid = transaction.savepoint()
                (rsvp, created) = RSVP.objects.get_or_create(event=self.object, person=request.user.person, canceled=False)
                rsvp = RSVP.objects.select_for_update().get(pk=rsvp.pk)

                if not created and not self.object.allow_guests:
                    transaction.savepoint_rollback(sid)
                    messages.add_message(
                        request=self.request,
                        level=messages.ERROR,
                        message="Cet événement ne permet pas d'inscrire des invité⋅e⋅s.",
                    )

                    return HttpResponseRedirect(reverse('view_event', args=[self.object.pk]))

                if submission and not created:
                    rsvp.guests_form_submissions.add(submission)
                    rsvp.guests = rsvp.guests_form_submissions.count()
                elif submission and created:
                    rsvp.form_submission = submission
                    unsaved_person.save()
                else:
                    rsvp.guests = guests

                rsvp.save()

                if self.object.max_participants and self.object.rsvps.aggregate(participants=Sum(F('guests') + 1))['participants'] > self.object.max_participants:
                    transaction.savepoint_rollback(sid)
                    messages.add_message(
                        request=self.request,
                        level=messages.ERROR,
                        message="La capacité maximum de cet événement a été atteinte. Vous ne pouvez plus vous inscrire.",
                    )
                    context = self.get_context_data(object=self.object)
                    return self.render_to_response(context)

            send_rsvp_notification.delay(rsvp.pk)
            return HttpResponseRedirect(reverse('view_event', kwargs={'pk': self.object.pk}))

        # if we're there, the event is paying
        if not self.object.allow_guests and self.object.rsvps.filter(person=request.user.person).exists():
            messages.add_message(
                request=self.request,
                level=messages.ERROR,
                message="Cet événement ne permet pas d'inscrire des invité⋅e⋅s.",
            )

            return HttpResponseRedirect(reverse('view_event', args=[self.object.pk]))

        if submission:
            request.session['rsvp_submission'] = submission.pk
        request.session['rsvp_event'] = str(self.object.pk)

        return HttpResponseRedirect(reverse('pay_event'))


class PayEventView(HardLoginRequiredMixin, UpdateView):
    form_class = BillingForm
    template_name = 'events/pay_event.html'

    def get_object(self, queryset=None):
        return self.request.user.person

    def get_context_data(self, **kwargs):
        if self.submission:
            form = self.submission.form.get_form()(self.request.user.person)
        kwargs.update({
            'event': self.event,
            'submission': self.submission,
            'price': self.event.get_price(self.submission)/100,
            'submission_data': {
                                    form.fields[id].label: value
                                    for id, value in self.submission.data.items()
                                } if self.submission else None
        })
        return super().get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        submission_pk = self.request.session.get('rsvp_submission')
        event_pk = self.request.session.get('rsvp_event')

        if not event_pk:
            return HttpResponseBadRequest('no event')

        try:
            self.event = Event.objects.upcoming().get(pk=event_pk)
        except Event.DoesNotExist:
            return HttpResponseBadRequest('no event')

        if self.event.subscription_form:
            if not submission_pk:
                return HttpResponseBadRequest('no submission')

            try:
                self.submission = PersonFormSubmission.objects.get(pk=submission_pk)
            except PersonFormSubmission.DoesNotExist:
                return HttpResponseBadRequest('no submission')
        else:
            self.submission = None

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['submission'] = self.submission
        kwargs['event'] = self.event
        return kwargs

    def form_valid(self, form):
        person = form.save()
        event = form.cleaned_data['event']
        submission = form.cleaned_data['submission']

        price = event.get_price(submission)

        return create_and_get_payment_response(
            person=person,
            type=EventsConfig.PAYMENT_TYPE,
            price=price,
            meta={'event_name': event.name, 'event_id': event and str(event.pk), 'submission_id': submission and str(submission.pk)}
        )


class PaidEventView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        payment = self.kwargs['payment']
        event = Event.objects.get(pk=self.kwargs['payment'].meta['event_id'])

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message=f"Votre paiement de {payment.price_display} pour l'événement « {event.name} » a bien été reçu. "
                    f"Votre inscription est confirmée."
        )
        return reverse('view_event', args=[self.kwargs['payment'].meta['event_id']])


def notification_listener(payment):
    # 500 error if

    if payment.status == Payment.STATUS_COMPLETED:
        submission_pk = payment.meta.get('submission_id')
        event_pk = payment.meta.get('event_id')

        # we don't check for cancellation of the event because we cant all actually paid rsvps to be registered in case
        # we need to manage refunding
        event = Event.objects.get(pk=event_pk)

        if event.subscription_form:
            if not submission_pk:
                return HttpResponseBadRequest('no submission')

            try:
                submission = PersonFormSubmission.objects.get(pk=submission_pk)
            except PersonFormSubmission.DoesNotExist:
                return HttpResponseBadRequest('no submission')
        else:
            submission = None

        with transaction.atomic():
            (rsvp, created) = RSVP.objects.get_or_create(
                person=payment.person,
                event=event
            )
            rsvp = RSVP.objects.select_for_update().get(pk=rsvp.pk)

            if submission and not created:
                rsvp.guests_form_submissions.add(submission)
                rsvp.guests = rsvp.guests_form_submissions.count()
            elif submission and created:
                rsvp.form_submission = submission
            elif not submission and not created:
                rsvp.guests = rsvp.guests + 1

            rsvp.save()
        send_rsvp_notification.delay(rsvp.pk)
