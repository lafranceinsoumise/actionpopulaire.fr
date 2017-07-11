from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import Http404

from people.models import Person
from events.models import Event, Calendar, RSVP
from groups.models import SupportGroup, Membership

from .forms import SimpleSubscriptionForm, OverseasSubscriptionForm, EventForm, SupportGroupForm
from .view_mixins import SuccessMessageView, LoginRequiredMixin, PermissionsRequiredMixin


class SubscriptionSuccessView(SuccessMessageView):
    title = "Merci de votre appui"
    message = """
    Votre soutien est bien enregistré. Vous serez tenu au courant de l'actualité du mouvement.
    """


class SimpleSubscriptionView(CreateView):
    template_name = "front/simple_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = SimpleSubscriptionForm


class OverseasSubscriptionView(CreateView):
    template_name = "front/overseas_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = OverseasSubscriptionForm


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
    success_url = reverse_lazy("create_event_success")
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


class UpdateEventView(LoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ('events.change_event',)
    template_name = "front/form.html"
    success_url = reverse_lazy("update_event_success")
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Modifiez votre événement')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendar'] = self.object.calendar
        return kwargs


class CreateEventSuccessView(SuccessMessageView):
    title = "Votre événement a bien été créé"
    message = """
    Pour revenir à votre 
    """


class UpdateEventSuccessView(SuccessMessageView):
    title = "Votre événement a été mis à jour"
    message = """
    Vous allez recevoir un mail vous permettant d'administrer votre nouvel événement.
    """


class SupportGroupListView(LoginRequiredMixin, ListView):
    """List person events
    """
    paginate_by = 20
    template_name = 'front/groups/list.html'
    context_object_name = 'memberships'

    def get_queryset(self):
        return Membership.objects.filter(person=self.request.user.person) \
            .select_related('supportgroup')


class CreateSupportGroupView(LoginRequiredMixin, CreateView):
    template_name = "front/form.html"
    success_url = reverse_lazy("list_groups")
    model = SupportGroup
    form_class = SupportGroupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Publiez votre événement')
        return context

    def get_success_url(self):
        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre groupe a été correctement créé.",
        )
        return super().get_success_url()


class UpdateSupportGroupView(LoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ('groups.change_supportgroup',)
    template_name = "front/form.html"
    success_url = reverse_lazy("list_groups")
    model = SupportGroup
    form_class = SupportGroupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Modifiez votre événement')
        return context

    def form_valid(self, form):
        # first get response to make sure there's no error before adding message
        res = super().form_valid(form)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Les modifications du groupe <em>%s</em> ont été enregistrées." % self.object.name,
        )

        return res


class QuitSupportGroupView(DeleteView):
    template_name = "front/groups/quit.html"
    success_url = reverse_lazy("list_groups")
    model = Membership
    context_object_name = 'membership'

    def get_object(self, queryset=None):
        try:
            return self.get_queryset().select_related('supportgroup').get(supportgroup__pk=self.kwargs['pk'])
        except Membership.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object.supportgroup
        context['success_url'] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        # first get response to make sure there's no error before adding message
        res = super().delete(request, *args, **kwargs)

        messages.add_message(
            request,
            messages.SUCCESS,
            _("Vous avez bien quitté le groupe <em>%s</em>" % self.object.supportgroup.name)
        )

        return res
