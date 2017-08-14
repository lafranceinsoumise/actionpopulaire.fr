from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.contrib import messages
from django.http import Http404
from django.core.urlresolvers import reverse_lazy

from groups.models import SupportGroup, Membership
from groups.tasks import send_support_group_changed_notification

from ..forms import SupportGroupForm
from ..view_mixins import LoginRequiredMixin, PermissionsRequiredMixin

__all__ = [
    "SupportGroupListView", "SupportGroupManagementView", "CreateSupportGroupView", "UpdateSupportGroupView",
    "QuitSupportGroupView"
]


class SupportGroupListView(LoginRequiredMixin, ListView):
    """List person support groups
    """
    paginate_by = 20
    template_name = 'front/groups/list.html'
    context_object_name = 'memberships'

    def get_queryset(self):
        return Membership.objects.filter(person=self.request.user.person) \
            .select_related('supportgroup')


class SupportGroupManagementView(DetailView):
    template_name = "front/groups/details.html"


class CreateSupportGroupView(LoginRequiredMixin, CreateView):
    template_name = "front/form.html"
    success_url = reverse_lazy("list_groups")
    model = SupportGroup
    form_class = SupportGroupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Publiez votre groupe d'appui")
        return context

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre groupe a été correctement créé.",
        )

        return res


class UpdateSupportGroupView(LoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ('groups.change_supportgroup',)
    template_name = "front/form.html"
    success_url = reverse_lazy("list_groups")
    model = SupportGroup
    form_class = SupportGroupForm

    CHANGES = {
        'name': "information",
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
        context['title'] = _("Modifiez votre groupe d'appui")
        return context

    def form_valid(self, form):
        # create set so that values are unique, but turns to list because set are not JSON-serializable
        changes = list({self.CHANGES[field] for field in form.changed_data})

        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        if changes:
            messages.add_message(
                request=self.request,
                level=messages.SUCCESS,
                message="Les modifications du groupe <em>%s</em> ont été enregistrées." % self.object.name,
            )

            send_support_group_changed_notification.delay(form.instance.pk, changes)

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
            # TODO show specific 404 page maybe?
            raise Http404()

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
