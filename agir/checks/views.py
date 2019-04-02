from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView


class CheckView(TemplateView):
    template_name = "checks/payment.html"
    order = None
    address = None
    additional_information = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            payment=kwargs["payment"],
            order=self.order,
            address=mark_safe(
                "<br>".join(conditional_escape(part) for part in self.address)
            ),
            additional_information=self.additional_information,
        )
