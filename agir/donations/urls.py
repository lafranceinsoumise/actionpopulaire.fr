from django.urls import path, include
from django.views.generic import RedirectView

from agir.donations import views

legacy_spending_request_urlpatterns = [
    path(
        "groupes/<uuid:group_id>/depenses/",
        RedirectView.as_view(pattern_name="create_group_spending_request"),
        name="create_spending_request",
    ),
    path(
        "financement/requete/<uuid:pk>/",
        RedirectView.as_view(pattern_name="spending_request_details"),
        name="manage_spending_request",
    ),
    path(
        "financement/requete/<uuid:pk>/modifier/",
        RedirectView.as_view(pattern_name="spending_request_update"),
        name="edit_spending_request",
    ),
    path(
        "financement/requete/<uuid:pk>/supprimer/",
        RedirectView.as_view(pattern_name="spending_request_details"),
        name="delete_spending_request",
    ),
    path(
        "financement/requete/<uuid:spending_request_id>/document/creer/",
        RedirectView.as_view(pattern_name="spending_request_details"),
        name="create_document",
    ),
    path(
        "financement/requete/<uuid:spending_request_id>/document/<int:pk>/",
        RedirectView.as_view(pattern_name="spending_request_details"),
        name="edit_document",
    ),
    path(
        "financement/requete/<uuid:spending_request_id>/document/<int:pk>/supprimer/",
        RedirectView.as_view(pattern_name="spending_request_details"),
        # views.DeleteDocumentView.as_view(),
        name="delete_document",
    ),
]

api_urlpatterns = [
    path(
        "dons/",
        views.CreateDonationAPIView.as_view(),
        name="api_donation_create",
    ),
    path(
        "financement/demande/",
        views.SpendingRequestCreateAPIView.as_view(),
        name="api_spending_request_create",
    ),
    path(
        "financement/demande/<uuid:pk>/",
        views.SpendingRequestRetrieveUpdateDestroyAPIView.as_view(),
        name="api_spending_request_retrieve_update_delete",
    ),
    path(
        "financement/demande/<uuid:pk>/document/",
        views.SpendingRequestDocumentCreateAPIView.as_view(),
        name="api_spending_request_document_create",
    ),
    path(
        "financement/document/<int:pk>/",
        views.SpendingRequestDocumentRetrieveUpdateDestroyAPIView.as_view(),
        name="api_spending_request_document_retrieve_update_delete",
    ),
    path(
        "financement/demande/<uuid:pk>/valider/",
        views.SpendingRequestApplyNextStatusAPIView.as_view(),
        name="api_spending_request_apply_next_status",
    ),
]

urlpatterns = [
    path(
        "dons-mensuels/deja-donateur/",
        views.AlreadyHasSubscriptionView.as_view(),
        name="already_has_subscription",
    ),
    path(
        "dons-mensuels/confirmer/attente/",
        views.MonthlyDonationEmailSentView.as_view(),
        name="monthly_donation_confirmation_email_sent",
    ),
    path(
        "dons-mensuels/confirmer/",
        views.MonthlyDonationEmailConfirmationView.as_view(),
        name="monthly_donation_confirm",
    ),
    path("", include(legacy_spending_request_urlpatterns)),
    path("api/", include(api_urlpatterns)),
]
