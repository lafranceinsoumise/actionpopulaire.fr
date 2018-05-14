from django.contrib.auth import authenticate, admin as auth_admin, BACKEND_SESSION_KEY
from django import forms
from django.contrib.redirects.admin import RedirectAdmin
from django.contrib.redirects.models import Redirect
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
import django_otp

class PersonAuthenticationForm(django_otp.admin.OTPAdminAuthenticationForm):
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
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        if len(self.device_choices(self.user_cache)) > 0:
            self.clean_otp(self.get_user())

        return self.cleaned_data


class APIAdminSite(django_otp.admin.OTPAdminSite):
    login_form = PersonAuthenticationForm
    site_header = 'France insoumise'
    site_title = 'France insoumise'
    index_title = 'Administration'

    def has_permission(self, request):
        return (
            super(django_otp.admin.OTPAdminSite, self).has_permission(request) and
            request.session[BACKEND_SESSION_KEY] == 'people.backend.PersonBackend'
            and (request.user.is_verified() or not django_otp.user_has_device(request.user))
        )

admin_site = APIAdminSite(django_otp.admin.OTPAdminSite.name)


# register auth
class DeviceAdmin(django_otp.plugins.otp_totp.admin.TOTPDeviceAdmin):
    list_display = ['email', 'name', 'confirmed', 'qrcode_link']

    def email(self, obj):
        return obj.user.person.email



admin_site.register(auth_admin.Group, auth_admin.GroupAdmin)
admin_site.register(Redirect, RedirectAdmin)
admin_site.register(Site, SiteAdmin)
admin_site.register(django_otp.plugins.otp_totp.models.TOTPDevice, DeviceAdmin)
