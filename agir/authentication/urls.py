from django.urls import path, include
from django.views.generic import TemplateView
from oauth2_provider import views as oauth2_views

from .views import (
    LoginView,
    CheckCodeView,
    DisconnectView,
    Oauth2AuthorizationView,
    SocialLoginError,
)


urlpatterns = [
    path("connexion/", LoginView.as_view(), name="short_code_login"),
    path("connexion/code/", CheckCodeView.as_view(), name="check_short_code",),
    path("deconnexion/", DisconnectView.as_view(), name="disconnect"),
    path("o/authorize/", Oauth2AuthorizationView.as_view(), name="authorize"),
    path("o/token/", oauth2_views.TokenView.as_view(), name="token"),
    path(
        "o/revoke_token/", oauth2_views.RevokeTokenView.as_view(), name="revoke-token"
    ),
    path(
        "o/introspect/", oauth2_views.IntrospectTokenView.as_view(), name="introspect"
    ),
    path("connexion/social/", include("social_django.urls", namespace="social")),
    path(
        "connexion/social/erreur/",
        SocialLoginError.as_view(),
        name="social_login_error",
    ),
]
