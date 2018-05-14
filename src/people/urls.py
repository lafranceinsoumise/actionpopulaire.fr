from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView

from . import views

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
simple_id = r'[0-9]+'


urlpatterns = [
    # people views
    url('^desinscription/$', views.UnsubscribeView.as_view(), name='unsubscribe'),
    url('^desabonnement/$', views.UnsubscribeView.as_view(), name='unsubscribe'),
    url('^desabonnement/succes/$', TemplateView.as_view(template_name='people/unsubscribe_success.html'), name='unsubscribe_success'),
    url('^supprimer/$', views.DeleteAccountView.as_view(), name='delete_account'),
    url('^supprimer/succes$', TemplateView.as_view(template_name='people/delete_account_success.html'), name='delete_account_success'),
    url('^inscription/$', views.SimpleSubscriptionView.as_view(), name='subscription'),
    url('^inscription/etranger/$', views.OverseasSubscriptionView.as_view(), name='subscription_overseas'),
    url('^inscription/succes/$', views.SubscriptionSuccessView.as_view(), name='subscription_success'),
    url('^profil/$', views.ChangeProfileView.as_view(), name='change_profile'),
    url('^profil/confirmation/$', views.ChangeProfileConfirmationView.as_view(), name='confirmation_profile'),
    url('^agir/$', views.VolunteerView.as_view(), name='volunteer'),
    url('^agir/confirmation/$', views.VolunteerConfirmationView.as_view(), name='confirmation_volunteer'),
    url('^message_preferences/$', views.MessagePreferencesView.as_view(), name='message_preferences'),
    url('^message_preferences/adresses/$', views.EmailManagementView.as_view(), name='email_management'),
    url(f'^message_preferences/adresses/(?P<pk>{simple_id})/supprimer/$', views.DeleteEmailAddressView.as_view(), name='delete_email'),
    url('^formulaires/(?P<slug>[-a-zA-Z0-9_]+)/$', views.PeopleFormView.as_view(), name='view_person_form'),
    url('^formulaires/(?P<slug>[-a-zA-Z0-9_]+)/confirmation/$', views.PeopleFormConfirmationView.as_view(), name='person_form_confirmation'),

    # dashboard
    url('^$', views.DashboardView.as_view(), name='dashboard'),
]
