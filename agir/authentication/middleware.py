from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext as _


class MailLinkMiddleware:
    @staticmethod
    def get_just_connected_message(user):
        return format_html(
            _("Bonjour {person} (ce n'est pas vous ? <a href=\"{login_url}\">Cliquez-ici pour vous reconnecter"
              "</a> avec votre compte.)"),
            person=user.person.get_short_name(),
            login_url=reverse('short_code_login')
        )

    @staticmethod
    def get_already_connected_message(current_user, link_user, link_url):
        return format_html(
            _("Vous êtes actuellement connecté comme {current_person}, mais vous avez suivi un lien qui a été envoyé"
              "à {link_person}. Souhaitez vous <a href=\"{link_url}\"> vous connecter comme {link_person} ?"),
            current_person=current_user.person.get_short_name(),
            link_person=link_user.person.get_short_name(),
            link_url=link_url
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
        if 'force_login' in other_params:
            del other_params['force_login']

        url = '{}?{}'.format(request.path, other_params.urlencode(safe='/')) if other_params else request.path

        link_user = authenticate(request, user_pk=request.GET['p'], token=request.GET['code'])

        # if we don't have any link_user, it means the link was forged or expired: we just ignore and redirect to
        # same url without the parameters
        if not link_user:
            return HttpResponseRedirect(url)

        force_login = request.GET.get('force_login')

        if request.user.is_anonymous or force_login:
            # we have a link_user, and current user is anonymous or asked for force_login ==> we log her in and redirect
            login(request, link_user)

            # session var used for external members joining a group or an event
            request.session['login_action'] = datetime.utcnow().timestamp()

            messages.add_message(
                request=request,
                level=messages.INFO,
                message=self.get_just_connected_message(link_user)
            )
        elif request.user != link_user:
            # we have a link_user, but current user is already logged in: we show a warning offering to connect with
            # link_user anyway
            params = request.GET.copy()
            params['force_login'] = 'yes'
            link_url = "{}?{}".format(request.path, params.urlencode(safe='/'))

            messages.add_message(
                request=request,
                level=messages.WARNING,
                message=self.get_already_connected_message(request.user, link_user, link_url)
            )

        return HttpResponseRedirect(url)
