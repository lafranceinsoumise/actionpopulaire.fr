from django.urls import path
from oauth2_provider import views as oauth2_views

from .views import SendEmailView, CheckCodeView, DisconnectView, Oauth2AuthorizationView


urlpatterns = [
    path('connexion/', SendEmailView.as_view(), name="short_code_login"),
    path('connexion/code/<uuid:user_pk>', CheckCodeView.as_view(), name="check_short_code"),
    path('deconnexion/', DisconnectView.as_view(), name='disconnect'),
    path('o/authorize/', Oauth2AuthorizationView.as_view(), name="authorize"),
    path('o/token/', oauth2_views.TokenView.as_view(), name="token"),
    path('o/revoke_token/', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
    path('o/introspect/', oauth2_views.IntrospectTokenView.as_view(), name="introspect"),
]
