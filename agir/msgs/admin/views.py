from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.generic import FormView

from agir.lib.admin.panels import AdminViewMixin
from agir.msgs.admin.forms import SupportGroupMessageCreateForm


class CreateAndSendSupportGroupMessageView(AdminViewMixin, FormView):
    template_name = "admin/supportgroupmessage/send.html"
    form_class = SupportGroupMessageCreateForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm("msgs.send_supportgroupmessage"):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        kwargs = {}
        if self.request.method in ["POST", "PUT"]:
            kwargs.update({"data": self.request.POST})

        return self.form_class(**kwargs)

    def get_context_data(self, **kwargs):
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()

        return super().get_context_data(
            title=_("Envoi d'un message de groupe"),
            change=True,
            add=False,
            save_as=False,
            show_save=True,
            show_save_and_continue=False,
            show_save_and_add_another=False,
            show_delete=False,
            **self.get_admin_helpers(
                kwargs["form"], kwargs["form"].fields, kwargs["form"].Meta.fieldsets
            ),
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            sent = form.save()
            if len(sent) == 0:
                messages.warning(request, "Aucun message n'a été crée ou envoyé")
            else:
                messages.success(
                    request,
                    ngettext(
                        _("Un message de groupe a été crée et envoyé"),
                        _(f"{len(sent)} messages de groupe ont été crées et envoyés"),
                        len(sent),
                    ),
                )
            return HttpResponseRedirect(
                reverse("admin:msgs_supportgroupmessage_changelist")
            )

        return TemplateResponse(
            request, self.template_name, context=self.get_context_data(form=form)
        )
