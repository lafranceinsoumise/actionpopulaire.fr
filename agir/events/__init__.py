from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import RedirectView

from agir.payments.abstract_payment_mode import AbstractPaymentMode

default_app_config = "agir.events.apps.EventsConfig"


class EventPayLaterView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        rsvp = getattr(self.kwargs["payment"], "rsvp")
        return reverse("rsvp_event", kwargs={"pk": rsvp.event.pk})


class PayLaterPaymentMode(AbstractPaymentMode):
    can_retry = False
    can_cancel = True

    id = "pay_later"
    label = "Poser une option et payer avant le 5 juillet"
    title = "Poser une option et payer avant le 5 juillet"

    def __init__(self):
        self.view = EventPayLaterView.as_view()

    @cached_property
    def payment_view(self):
        return self.view
