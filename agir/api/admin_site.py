import locale

import django_otp
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, BACKEND_SESSION_KEY
from django.utils.translation import gettext_lazy as _
from django_otp.admin import OTPAdminAuthenticationForm, OTPAdminSite


class PersonAuthenticationForm(OTPAdminAuthenticationForm):
    username = forms.EmailField(
        label=_("Adresse email"), widget=forms.EmailInput(attrs={"autofocus": True})
    )

    password = forms.CharField(
        label=_("Mot de passe"), strip=False, widget=forms.PasswordInput
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        self.fields["username"].max_length = None
        self.fields["username"].widget.attrs["maxlength"] = None

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                    params={"username": self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        if len(self.device_choices(self.user_cache)) > 0:
            self.clean_otp(self.get_user())

        return self.cleaned_data


class APIAdminSite(OTPAdminSite):
    login_form = PersonAuthenticationForm
    site_header = "Action populaire"
    site_title = "Action populaire"
    index_title = "Administration"

    def __init__(self, name=OTPAdminSite.name):
        super(APIAdminSite, self).__init__(name=name)

    def has_permission(self, request):
        return (
            super(OTPAdminSite, self).has_permission(request)
            and request.session[BACKEND_SESSION_KEY]
            == "agir.people.backend.PersonBackend"
            and (
                request.user.is_verified()
                or not django_otp.user_has_device(request.user)
            )
        )

    def each_context(self, request):
        return {
            "production_colors": settings.ADMIN_PRODUCTION,
            **super().each_context(request),
        }

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site, using the default collation
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(
            app_dict.values(), key=lambda x: locale.strxfrm(str(x["name"].lower()))
        )

        # Sort the models alphabetically within each app.
        for app in app_list:
            app["models"].sort(key=lambda x: locale.strxfrm(str(x["name"])))

        return app_list
