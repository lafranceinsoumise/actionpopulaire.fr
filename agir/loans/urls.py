from django.urls import path

from agir.loans.views import LoanContractView

urlpatterns = [
    path(
        "contrat/<int:pk>/",
        LoanContractView.as_view(),
        name="loans_view_contract",
    )
]
