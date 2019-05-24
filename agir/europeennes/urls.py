from django.urls import re_path, reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [
    re_path(
        "^europeennes/.*",
        RedirectView.as_view(url=reverse_lazy("donation_amount")),
        name="europeennes_donation_and_loan",
    )
]
