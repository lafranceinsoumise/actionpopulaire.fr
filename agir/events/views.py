import json
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import F, Sum
from django.views.generic import CreateView, UpdateView, TemplateView, DeleteView, DetailView, FormView
from django.views.generic.edit import ProcessFormView, FormMixin
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from django.utils.translation import ugettext as _

from .apps import EventsConfig
from .models import Event, RSVP, Calendar, EventSubtype
from .tasks import send_cancellation_notification, send_rsvp_notification
from ..people.models import PersonFormSubmission
from ..payments.actions import get_payment_response
from ..payments.models import Payment

from .forms import (
    EventForm, AddOrganizerForm, EventGeocodingForm, EventReportForm, UploadEventImageForm, AuthorForm, SearchEventForm,
    BillingForm,
    GuestsForm)
from ..front.view_mixins import (
    HardLoginRequiredMixin, SoftLoginRequiredMixin, PermissionsRequiredMixin, ObjectOpengraphMixin,
    ChangeLocationBaseView, SearchByZipcodeBaseView,
)

__all__ = [
    'CreateEventView', 'ManageEventView', 'ModifyEventView', 'QuitEventView', 'CancelEventView',
    'EventDetailView', 'CalendarView', 'ChangeEventLocationView', 'EditEventReportView', 'UploadEventImageView',
    'EventListView', 'PerformCreateEventView'
]


class EventListView(SearchByZipcodeBaseView):
    """List of events, filter by zipcode
    """
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    form_class = SearchEventForm

    def get_base_queryset(self):
        return Event.objects.upcoming().order_by('start_time')


class EventDetailView(ObjectOpengraphMixin, DetailView):
    template_name = "events/detail.html"
    queryset = Event.objects.filter(published=True)

    title_prefix = _("Evénement local")
    meta_description = _("Participez aux événements organisés par les membres de la France insoumise.")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            rsvp=self.request.user.is_authenticated and self.object.rsvps.filter(
                person=self.request.user.person).first(),
            is_organizer=self.request.user.is_authenticated and self.object.organizers.filter(
                pk=self.request.user.person.id).exists(),
            organizers_groups=self.object.organizers_groups.distinct(),
            event_images=self.object.images.all(),
        )


class ManageEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, DetailView):
    template_name = "events/manage.html"
    permissions_required = ('events.change_event',)
    queryset = Event.objects.filter(published=True)

    error_messages = {
        'denied': _("Vous ne pouvez pas accéder à cette page sans être organisateur de l'événement.")
    }

    def get_success_url(self):
        return reverse('manage_event', kwargs={'pk': self.object.pk})

    def get_form(self):
        kwargs = {}

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
            })

        return AddOrganizerForm(self.object, **kwargs)

    def get_context_data(self, **kwargs):
        if 'add_organizer_form' not in kwargs:
            kwargs['add_organizer_form'] = self.get_form()

        return super().get_context_data(
            organizers=self.object.organizers.all(),
            rsvps=self.object.rsvps.all(),
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_past():
            raise PermissionDenied(_('Vous ne pouvez pas ajouter d\'organisateur à un événement terminé.'))

        form = self.get_form()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(add_organizer_form=form))


class CreateEventView(SoftLoginRequiredMixin, TemplateView):
    template_name = "events/create.html"

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        groups = [{'id': str(m.supportgroup.pk), 'name': m.supportgroup.name}
                  for m in person.memberships.filter(is_manager=True)]

        initial = {
            'email': person.email
        }

        if person.contact_phone:
            initial['phone'] = person.contact_phone.as_e164

        if person.first_name and person.last_name:
            initial['name'] = '{} {}'.format(person.first_name, person.last_name)

        initial_group = self.request.GET.get('group')
        if initial_group in [g['id'] for g in groups]:
            initial['organizerGroup'] = initial_group

        subtype_label = self.request.GET.get('subtype')
        if subtype_label:
            try:
                subtype = EventSubtype.objects.get(label=subtype_label)
                initial['subtype'] = subtype.label
            except EventSubtype.DoesNotExist:
                pass

        return super().get_context_data(
            props=mark_safe(json.dumps({'initial': initial, 'groups': groups})),
            **kwargs
        )


class PerformCreateEventView(SoftLoginRequiredMixin, FormMixin, ProcessFormView):
    model = Event
    form_class = EventForm

    def get_form_kwargs(self):
        """Add user person profile to the form kwargs"""

        kwargs = super().get_form_kwargs()

        person = self.request.user.person
        kwargs['person'] = person
        return kwargs

    def form_invalid(self, form):
        return JsonResponse({'errors': form.errors}, status=400)

    def form_valid(self, form):
        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre événement a été correctement créé.",
        )

        form.save()

        return JsonResponse({
            'status': 'OK',
            'id': form.instance.id,
            'url': reverse('view_event', args=[form.instance.id])
        })


class ModifyEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ('events.change_event',)
    template_name = "events/modify.html"
    form_class = EventForm

    def get_success_url(self):
        return reverse('manage_event', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['person'] = self.request.user.person
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Modifiez votre événement')
        return context

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message=format_html(_("Les modifications de l'événement <em>{}</em> ont été enregistrées."),
                                self.object.name)
        )

        return res


class CancelEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, DetailView):
    permissions_required = ('events.change_event',)
    template_name = 'events/cancel.html'
    success_url = reverse_lazy('list_events')

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.published = False
        self.object.save()

        send_cancellation_notification.delay(self.object.pk)

        messages.add_message(
            request,
            messages.WARNING,
            _("L'événement « {} » a bien été annulé.").format(self.object.name)
        )

        return HttpResponseRedirect(self.success_url)


class QuitEventView(SoftLoginRequiredMixin, DeleteView):
    template_name = "events/quit.html"
    success_url = reverse_lazy("list_events")
    context_object_name = 'rsvp'

    def get_queryset(self):
        return RSVP.objects.upcoming(as_of=timezone.now())

    def get_object(self, queryset=None):
        try:
            return self.get_queryset().select_related('event').get(
                event__pk=self.kwargs['pk'],
                person=self.request.user.person
            )
        except RSVP.DoesNotExist:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.object.event
        context['success_url'] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        # first get response to make sure there's no error before adding message
        res = super().delete(request, *args, **kwargs)

        messages.add_message(
            request,
            messages.SUCCESS,
            format_html(_("Vous ne participez plus à l'événement <em>{}</em>"), self.object.event.name)
        )

        return res


class CalendarView(ObjectOpengraphMixin, DetailView):
    template_name = "events/calendar.html"
    model = Calendar
    paginator_class = Paginator
    per_page = 10

    def get_context_data(self, **kwargs):
        all_events = self.object.events.upcoming(as_of=timezone.now()).order_by('start_time')
        paginator = self.paginator_class(all_events, self.per_page)

        page = self.request.GET.get('page')
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        return super().get_context_data(
            events=events,
            default_event_image=settings.DEFAULT_EVENT_IMAGE,
        )


class ChangeEventLocationView(ChangeLocationBaseView):
    template_name = 'events/change_location.html'
    form_class = EventGeocodingForm
    success_view_name = 'manage_event'

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now())


class EditEventReportView(PermissionsRequiredMixin, UpdateView):
    template_name = 'events/edit_event_report.html'
    permissions_required = ('events.change_event',)
    form_class = EventReportForm

    def get_success_url(self):
        return reverse('manage_event', args=(self.object.pk,))

    def get_queryset(self):
        return Event.objects.past(as_of=timezone.now())


class UploadEventImageView(CreateView):
    template_name = 'events/upload_event_image.html'
    form_class = UploadEventImageForm

    def get_queryset(self):
        return Event.objects.past(as_of=timezone.now())

    def get_success_url(self):
        return reverse('view_event', args=(self.event.pk,))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'author': self.request.user.person,
            'event': self.event
        })
        return kwargs

    def get_author_form(self):
        author_form_kwargs = {
            'instance': self.request.user.person,
        }
        if self.request.method in ['POST', 'PUT']:
            author_form_kwargs['data'] = self.request.POST

        return AuthorForm(**author_form_kwargs)

    def get_context_data(self, **kwargs):
        if 'author_form' not in kwargs:
            kwargs['author_form'] = self.get_author_form()

        return super().get_context_data(
            event=self.event,
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.object = None
        self.event = self.get_object()

        if not self.event.rsvps.filter(person=request.user.person).exists():
            raise PermissionDenied(_("Seuls les participants à l'événement peuvent poster des images"))

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.event = self.get_object()

        if not self.event.rsvps.filter(person=request.user.person).exists():
            raise PermissionDenied(_("Seuls les participants à l'événement peuvent poster des images"))

        form = self.get_form()
        author_form = self.get_author_form()

        if form.is_valid() and author_form.is_valid():
            return self.form_valid(form, author_form)
        else:
            return self.form_invalid(form, author_form)

    def form_invalid(self, form, author_form):
        return self.render_to_response(self.get_context_data(form=form, author_form=author_form))

    def form_valid(self, form, author_form):
        author_form.save()
        form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Votre photo a correctement été importée, merci de l'avoir partagée !")
        )

        return HttpResponseRedirect(self.get_success_url())


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

        return form_class(**kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=self.get_form(),
            event=self.object,
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.rsvps.filter(person=request.user.person, canceled=False).exists():
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
                form.save()
                submission = form.submission
            else:
                context = self.get_context_data(object=self.object)
                return self.render_to_response(context)

        if self.object.payment_parameters is None:
            with transaction.atomic():
                sid = transaction.savepoint()
                (rsvp, created) = RSVP.objects.get_or_create(event=self.object, person=request.user.person, canceled=False)
                rsvp.form_submission = submission
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

        else:
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

        return get_payment_response(
            person=person,
            type=EventsConfig.PAYMENT_TYPE,
            price=price,
            meta={'event_name': event.name, 'event_id': str(event.pk), 'submission_id': str(submission.pk)}
        )


class PaidEventView(TemplateView):
    template_name = 'events/payment_confirmation.html'

    def get_context_data(self, **kwargs):
        return {
            'payment': self.kwargs['payment'],
            'event': Event.objects.get(pk=self.kwargs['payment'].meta['event_id'])
        }


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

        rsvp = RSVP.objects.create(
            person=payment.person,
            event=event,
            form_submission=submission
        )
        send_rsvp_notification.delay(rsvp.pk)
