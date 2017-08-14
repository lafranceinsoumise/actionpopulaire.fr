from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import Http404

from events.models import Event, Calendar, RSVP
from events.tasks import send_event_changed_notification

from ..forms import EventForm
from ..view_mixins import LoginRequiredMixin, PermissionsRequiredMixin

__all__ = [
    "EventListView", "CreateEventView", "UpdateEventView", "QuitEventView"
]


class EventListView(LoginRequiredMixin, ListView):
    """List person events
    """
    paginate_by = 20
    template_name = 'front/events/list.html'
    context_object_name = 'events'

    queryset = Event.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rsvps'] = self.get_rsvps()
        return context

    def get_queryset(self):
        return self.queryset.filter(organizers=self.request.user.person)

    def get_rsvps(self):
        return RSVP.objects.select_related('event').filter(person=self.request.user.person)


class CreateEventView(LoginRequiredMixin, CreateView):
    template_name = "front/form.html"
    success_url = reverse_lazy("list_events")
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Publiez votre événement')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendar'] = Calendar.objects.get(label='evenements_locaux')
        return kwargs

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre événement a été correctement créé.",
        )

        return res


class UpdateEventView(LoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ('events.change_event',)
    template_name = "front/form.html"
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendar'] = self.object.calendar
        return kwargs

    def form_valid(self, form):
        # create set so that values are unique, but turns to list because set are not JSON-serializable
        changes = list({self.CHANGES[field] for field in form.changed_data})

        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        if changes:
            messages.add_message(
                request=self.request,
                level=messages.SUCCESS,
                message="Les modifications de l'événement <em>%s</em> ont été enregistrées." % self.object.name,
            )

            send_event_changed_notification.delay(form.instance.pk, changes)

        return res


class QuitEventView(DeleteView):
    template_name = "front/events/quit.html"
    success_url = reverse_lazy("list_events")
    model = RSVP
    context_object_name = 'rsvp'

    def get_object(self, queryset=None):
        try:
            return self.get_queryset().select_related('event').get(event__pk=self.kwargs['pk'])
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
            _("Vous ne participez plus à l'événement <em>%s</em>" % self.object.supportgroup.name)
        )

        return res
