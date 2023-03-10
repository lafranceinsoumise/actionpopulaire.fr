from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from agir.lib.utils import front_url


class CheckView(TemplateView):
    template_name = "checks/payment.html"
    title = None
    order = None
    address = None
    additional_information = None
    warnings = None

    def get_context_data(self, **kwargs):
        payment = kwargs["payment"]

        if self.request.GET.get("next") == "profile":
            next_url = front_url("view_payments")
        else:
            next_url = front_url("payment_return", args=(payment.pk,))

        return super().get_context_data(
            payment=payment,
            title=self.title,
            order=self.order,
            address=mark_safe(
                "<br>".join(conditional_escape(part) for part in self.address)
            ),
            additional_information=self.additional_information,
            warnings=self.warnings,
            next_url=next_url,
        )

    def get(self, request, *args, **kwargs):
        from agir.checks.tasks import send_check_information

        send_check_information.delay(kwargs["payment"].id)
        return super().get(request, *args, **kwargs)
