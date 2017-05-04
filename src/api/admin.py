from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from django.utils.translation import ugettext_lazy as _


class APIAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('Adresse email'),
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    password = forms.CharField(
        label=_('Mot de passe'),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(APIAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.email_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class APIAdminSite(AdminSite):
    login_form = APIAuthenticationForm


admin_site = APIAdminSite()