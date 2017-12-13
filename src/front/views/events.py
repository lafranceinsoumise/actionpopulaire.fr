from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from events.models import Event, RSVP, Calendar
from events.tasks import send_cancellation_notification, send_rsvp_notification

from ..forms import EventForm, AddOrganizerForm, EventGeocodingForm, EventReportForm, UploadEventImageForm, AuthorForm
from ..view_mixins import (
    HardLoginRequiredMixin, SoftLoginRequiredMixin, PermissionsRequiredMixin, ObjectOpengraphMixin,
    ChangeLocationBaseView
)

__all__ = [
    'EventListView', 'CreateEventView', 'ManageEventView', 'ModifyEventView', 'QuitEventView', 'CancelEventView',
    'EventDetailView', 'CalendarView', 'ChangeEventLocationView', 'EditEventReportView', 'UploadEventImageView'
]


class EventListView(SoftLoginRequiredMixin, ListView):
    """List person events
    """
    paginate_by = 20
    template_name = 'front/events/list.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rsvps'] = self.get_rsvps()
        context['past_events'] = self.get_past_events()
        return context

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now()).filter(organizers=self.request.user.person)

    def get_rsvps(self):
        return RSVP.objects.upcoming(as_of=timezone.now()).select_related('event').filter(
            person=self.request.user.person)

    def get_past_events(self):
        return Event.objects.past(as_of=timezone.now()).filter(rsvps__person=self.request.user.person).order_by(
            '-start_time')


class EventDetailView(ObjectOpengraphMixin, DetailView):
    template_name = "front/events/detail.html"
    queryset = Event.objects.filter(published=True)

    title_prefix = _("Evénement local")
    meta_description = _("Participez aux événements organisés par les membres de la France insoumise.")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            has_rsvp=self.request.user.is_authenticated and self.object.rsvps.filter(person=self.request.user.person).exists(),
            is_organizer=self.request.user.is_authenticated and self.object.organizers.filter(pk=self.request.user.person.id).exists(),
            organizers_groups=self.object.organizers_groups.distinct(),
            event_images=self.object.images.all(),
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


class ManageEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, DetailView):
    template_name = "front/events/manage.html"
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
        return super().get_context_data(
            add_organizer_form=self.get_form(),
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
    form_class = EventForm

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
    template_name = 'front/events/cancel.html'
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
    template_name = "front/events/quit.html"
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
    template_name = 'front/events/change_location.html'
    form_class = EventGeocodingForm
    success_view_name = 'manage_event'

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now())


class EditEventReportView(PermissionsRequiredMixin, UpdateView):
    template_name = 'front/events/edit_event_report.html'
    permissions_required = ('events.change_event',)
    form_class = EventReportForm

    def get_success_url(self):
        return reverse('manage_event', args=(self.object.pk,))

    def get_queryset(self):
        return Event.objects.past(as_of=timezone.now())


class UploadEventImageView(CreateView):
    template_name = 'front/events/upload_event_image.html'
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
