from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from agir.authentication.models import Role


class MailLinkMiddleware():
    @staticmethod
    def get_message_string(user):
        return format_html(
            _("Bonjour {person} (ce n'est pas vous ? <a href=\"{login_url}\">Cliquez-ici pour vous reconnecter"
              "</a> avec votre compte.)"),
            person=user.person.get_short_name(),
            login_url=reverse('oauth_redirect_view')
        )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not ('p' in request.GET and 'code' in request.GET):
            return self.get_response(request)

        # preserve other query params than p and code when we redirect
        other_params = request.GET.copy()
        del other_params['p']
        del other_params['code']
        url = '{}?{}'.format(request.path, other_params.urlencode(safe='/')) if other_params else request.path

        user = authenticate(user_pk=request.GET['p'], code=request.GET['code'])

        # case where user is already authenticated and different from user above ==> redirect with warning message
        if request.user.is_authenticated and request.user != user:
            messages.add_message(
                request=request,
                level=messages.WARNING,
                message=self.get_message_string(request.user)
            )
            return HttpResponseRedirect(url)
        # case where user is being authenticated ==> we show a message but only with info level
        elif user:
            login(request, user)
            messages.add_message(
                request=request,
                level=messages.INFO,
                message=self.get_message_string(user)
            )
            return HttpResponseRedirect(url)


class KnownEmailCookieMiddleWare():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not request.user.is_authenticated:
            return response

        if not (hasattr(request.user, 'type') and request.user.type == Role.PERSON_ROLE):
            return response

        domain = '.'.join(request.META.get('HTTP_HOST', '').split('.')[-2:])

        emails_cookie = request.COOKIES.get('knownEmails')
        emails = emails_cookie.split(',') if emails_cookie is not None else []

        if request.user.person.email in emails:
            emails.remove(request.user.person.email)
        emails.insert(0, request.user.person.email)

        response.set_cookie('knownEmails', value=','.join(emails[0:4]), max_age=365, domain=domain, secure=True, httponly=True)

        return response
