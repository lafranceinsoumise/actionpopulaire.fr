from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

from events.models import Event, RSVP, OrganizerConfig, Calendar, published_event_only
from events.tasks import send_cancellation_notification, send_rsvp_notification

from ..forms import EventForm, AddOrganizerForm, EventGeocodingForm
from ..view_mixins import (
    HardLoginRequiredMixin, SoftLoginRequiredMixin, PermissionsRequiredMixin, ObjectOpengraphMixin,
    ChangeLocationBaseView
)

__all__ = [
    'EventListView', 'CreateEventView', 'ManageEventView', 'ModifyEventView', 'QuitEventView', 'CancelEventView',
    'EventDetailView', 'CalendarView', 'ChangeEventLocationView'
]


class IsOrganiserMixin:
    def is_organizer(self):
        event = self.object if isinstance(self.object, Event) else self.object.event
        return OrganizerConfig.objects.filter(person=self.request.user.person, event=event).exists()


class EventListView(SoftLoginRequiredMixin, ListView):
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
        return RSVP.current.select_related('event').filter(person=self.request.user.person)


class EventDetailView(ObjectOpengraphMixin, DetailView):
    template_name = "front/events/detail.html"
    queryset = Event.scheduled.all()

    title_prefix = _("Evénement local")
    meta_description = _("Participez aux événements organisés par les membres de la France insoumise.")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            has_rsvp=self.request.user.is_authenticated and self.object.rsvps.filter(person=self.request.user.person).exists(),
            is_organizer=self.request.user.is_authenticated and self.object.organizers.filter(pk=self.request.user.person.id).exists()
        )

    @method_decorator(login_required(login_url=reverse_lazy('oauth_redirect_view')), )
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.POST['action'] == 'rsvp':
            if not self.object.rsvps.filter(person=request.user.person).exists():
                rsvp = RSVP.objects.create(event=self.object, person=request.user.person)
                send_rsvp_notification.delay(rsvp.pk)
            return HttpResponseRedirect(reverse('view_event', kwargs={'pk': self.object.pk}))

        return HttpResponseBadRequest()


class ManageEventView(HardLoginRequiredMixin, IsOrganiserMixin, DetailView):
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


class CreateEventView(HardLoginRequiredMixin, CreateView):
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
        kwargs['initial'] = {
            'contact_name': person.get_full_name(),
            'contact_email': person.email,
            'contact_phone': person.contact_phone,
        }
        kwargs['person'] = person

        return kwargs

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        # show message
        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre événement a été correctement créé.",
        )

        return res


class ModifyEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ('events.change_event',)
    template_name = "front/events/modify.html"
    success_url = reverse_lazy("list_events")
    model = Event
    form_class = EventForm

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
            message=format_html(_("Les modifications de l'événement <em>{}</em> ont été enregistrées."), self.object.name)
        )

        return res


class CancelEventView(HardLoginRequiredMixin, DetailView):
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


class QuitEventView(SoftLoginRequiredMixin, DeleteView):
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
            format_html(_("Vous ne participez plus à l'événement <em>{}</em>"), self.object.event.name)
        )

        return res


class CalendarView(ObjectOpengraphMixin, DetailView):
    template_name = "front/events/calendar.html"
    model = Calendar
    paginator_class = Paginator
    per_page = 10

    def get_context_data(self, **kwargs):
        all_events = self.object.events.filter(published_event_only()).order_by('start_time')
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
    template_name = 'front/events/change_location.html'
    form_class = EventGeocodingForm
    queryset = Event.scheduled.all()
    success_view_name = 'manage_event'
