from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView


class CheckView(TemplateView):
    template_name = "checks/payment.html"
    title = None
    order = None
    address = None
    additional_information = None
    warnings = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            payment=kwargs["payment"],
            title=self.title,
            order=self.order,
            address=mark_safe(
                "<br>".join(conditional_escape(part) for part in self.address)
            ),
            additional_information=self.additional_information,
            warnings=self.warnings,
        )

    def get(self, request, *args, **kwargs):
        from agir.checks.tasks import send_check_information

        send_check_information.delay(kwargs["payment"].id)
        return super().get(request, *args, **kwargs)
