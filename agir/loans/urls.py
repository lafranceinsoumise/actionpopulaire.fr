from django.urls import path

from agir.loans.views import LoanContractView

urlpatterns = [
    path(
        "prets/<int:pk>/contrat/",
        LoanContractView.as_view(),
        name="loans_view_contract",
    )
]
