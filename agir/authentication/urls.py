from django.urls import path, include
from oauth2_provider import views as oauth2_views

from .views import (
    CSRFAPIView,
    Oauth2AuthorizationView,
    SocialLoginError,
    SessionContextAPIView,
    LoginAPIView,
    CheckCodeAPIView,
    LogoutAPIView,
)


urlpatterns = [
    path("api/csrf/", CSRFAPIView.as_view(), name="api_csrf"),
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
    path("api/session/", SessionContextAPIView.as_view(), name="api_session"),
    path("api/connexion/", LoginAPIView.as_view(), name="api_login"),
    path("api/connexion/code/", CheckCodeAPIView.as_view(), name="api_check_code"),
    path("api/deconnexion/", LogoutAPIView.as_view(), name="api_logout"),
]
