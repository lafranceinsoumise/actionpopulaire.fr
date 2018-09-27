from django.urls import path

from .views import SendEmailView, CheckCodeView, DisconnectView


urlpatterns = [
    path('connexion/', SendEmailView.as_view(), name="short_code_login"),
    path('connexion/code/<uuid:user_pk>', CheckCodeView.as_view(), name="check_short_code"),
    path('deconnexion/', DisconnectView.as_view(), name='disconnect')
]
