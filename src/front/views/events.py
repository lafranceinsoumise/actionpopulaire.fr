from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.db import transaction

from events.models import Event, Calendar, RSVP, OrganizerConfig
from events.tasks import send_event_changed_notification, send_cancellation_notification

from ..forms import EventForm, AddOrganizerForm
from ..view_mixins import LoginRequiredMixin, PermissionsRequiredMixin

__all__ = [
    "EventListView", "CreateEventView", "ManageEventView", "ModifyEventView", "QuitEventView", "CancelEventView",
    "EventDetailView"
]


class IsOrganiserMixin:
    def is_organizer(self):
        event = self.object if isinstance(self.object, Event) else self.object.event
        return OrganizerConfig.objects.filter(person=self.request.user.person, event=event).exists()


class EventListView(LoginRequiredMixin, ListView):
    """List person events
    """
    paginate_by = 20
    template_name = 'front/events/list.html'
    context_object_name = 'events'

    queryset = Event.scheduled.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rsvps'] = self.get_rsvps()
        return context

    def get_queryset(self):
        return self.queryset.filter(organizers=self.request.user.person)

    def get_rsvps(self):
        return RSVP.objects.select_related('event').filter(person=self.request.user.person)


class EventDetailView(DetailView):
    template_name = "front/events/detail.html"
    queryset = Event.scheduled.all()


class ManageEventView(LoginRequiredMixin, IsOrganiserMixin, DetailView):
    template_name = "front/events/manage.html"
    queryset = Event.scheduled.all()

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
        return super().get_context_data(
            add_organizer_form=self.get_form(),
            organizers=self.object.organizers.all(),
            rsvps=self.object.rsvps.all()
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.is_organizer():
            return HttpResponseForbidden(b'Interdit')

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.is_organizer():
            return HttpResponseForbidden(b'Interdit')

        form = self.get_form()

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CreateEventView(LoginRequiredMixin, CreateView):
    template_name = "front/events/create.html"
    model = Event
    form_class = EventForm

    def get_success_url(self):
        return reverse('manage_event', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Publiez votre événement')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        person = self.request.user.person
        kwargs['calendar'] = Calendar.objects.get(label='evenements_locaux')
        kwargs['initial'] = {
            'contact_name': person.get_full_name(),
            'contact_email': person.email,
            'contact_phone': person.contact_phone
        }
        return kwargs

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        with transaction.atomic():
            self.object = form.save()

            OrganizerConfig.objects.create(
                person=self.request.user.person,
                event=self.object
            )

            RSVP.objects.create(
                person=self.request.user.person,
                event=self.object,
            )

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre événement a été correctement créé.",
        )

        return HttpResponseRedirect(self.get_success_url())


class ModifyEventView(LoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ('events.change_event',)
    template_name = "front/events/modify.html"
    success_url = reverse_lazy("list_events")
    model = Event
    form_class = EventForm

    CHANGES = {
        'name': "information",
        'start_time': "timing",
        'end_time': "timing",
        'contact_name': "contact",
        'contact_email': "contact",
        'contact_phone': "contact",
        'location_name': "location",
        'location_address1': "location",
        'location_address2': "location",
        'location_city': "location",
        'location_zip': "location",
        'location_country': "location",
        'description': "information"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Modifiez votre événement')
        return context

    def form_valid(self, form):
        # create set so that values are unique, but turns to list because set are not JSON-serializable
        changes = list({self.CHANGES[field] for field in form.changed_data if field in self.CHANGES})

        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        if changes and form.cleaned_data['notify']:
            send_event_changed_notification.delay(form.instance.pk, changes)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Les modifications de l'événement <em>%s</em> ont été enregistrées." % self.object.name,
        )

        return res


class CancelEventView(LoginRequiredMixin, DetailView):
    template_name = 'front/events/cancel.html'
    queryset = Event.scheduled.all()
    success_url = reverse_lazy('list_events')

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


class QuitEventView(LoginRequiredMixin, DeleteView):
    template_name = "front/events/quit.html"
    success_url = reverse_lazy("list_events")
    model = RSVP
    context_object_name = 'rsvp'

    def get_object(self, queryset=None):
        try:
            return self.get_queryset().select_related('event').get(
                event__pk=self.kwargs['pk'],
                person=self.request.user.person
            )
        except RSVP.DoesNotExist:
            # TODO show specific 404 page maybe?
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
            _("Vous ne participez plus à l'événement <em>%s</em>" % self.object.event.name)
        )

        return res
