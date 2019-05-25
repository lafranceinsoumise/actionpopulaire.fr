from django.urls import re_path, reverse_lazy, path
from django.views.generic import RedirectView

from agir.europeennes import views

urlpatterns = [
    path(
        "europennes/prets/contrat/<int:pk>/",
        views.LoanContractView.as_view(),
        name="europeennes_view_contract",
    ),
    re_path(
        "^europeennes/.*",
        RedirectView.as_view(url=reverse_lazy("donation_amount")),
        name="europeennes_donation_and_loan",
    ),
]
