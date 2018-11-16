from django.urls import path
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    # people views
    path('desinscription/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    path('desabonnement/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    path('desabonnement/succes/', TemplateView.as_view(template_name='people/unsubscribe_success.html'), name='unsubscribe_success'),
    path('supprimer/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('supprimer/succes', TemplateView.as_view(template_name='people/delete_account_success.html'), name='delete_account_success'),
    path('inscription/', views.SimpleSubscriptionView.as_view(), name='subscription'),
    path('inscription/etranger/', views.OverseasSubscriptionView.as_view(), name='subscription_overseas'),
    path('inscription/attente/', views.ConfirmationMailSentView.as_view(), name='subscription_mail_sent'),
    path('inscription/confirmer/', views.ConfirmSubscriptionView.as_view(), name='subscription_confirm'),
    path('profil/', views.ChangeProfileView.as_view(), name='change_profile'),
    path('profil/confirmation/', views.ChangeProfileConfirmationView.as_view(), name='confirmation_profile'),
    path('agir/', views.VolunteerView.as_view(), name='volunteer'),
    path('agir/confirmation/', views.VolunteerConfirmationView.as_view(), name='confirmation_volunteer'),
    path('message_preferences/', views.MessagePreferencesView.as_view(), name='message_preferences'),
    path('message_preferences/adresses/', views.EmailManagementView.as_view(), name='email_management'),
    path('message_preferences/adresses/<int:pk>/supprimer/', views.DeleteEmailAddressView.as_view(), name='delete_email'),
    path('formulaires/<slug:slug>/', views.PeopleFormView.as_view(), name='view_person_form'),
    path('formulaires/<slug:slug>/edit/<pk>', views.PeopleFormEditSubmissionView.as_view(), name='edit_person_form_submission'),
    path('formulaires/<slug:slug>/confirmation/', views.PeopleFormConfirmationView.as_view(), name='person_form_confirmation'),
    path('telephone/sms', views.SendValidationSMSView.as_view(), name='send_validation_sms'),
    path('telephone/validation', views.CodeValidationView.as_view(), name='sms_code_validation'),

    # dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
]
