from django.views.generic import TemplateView

from .models import CheckPayment


class CheckView(TemplateView):
    queryset = CheckPayment.objects.all()
    template_name = 'checks/payment.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            payment=kwargs['payment']
        )
