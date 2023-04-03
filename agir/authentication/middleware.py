from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _


class MailLinkMiddleware:
    @staticmethod
    def get_just_connected_message(user):
        return format_html(
            _(
                '<p class="padbottom">Vous avez été connecté automatiquement comme <b>{person}</b> car vous avez suivi un lien qui lui a'
                ' été envoyé par email.</p> <a href="{logout_url}?next={login_url}">'
                "<strong>Je ne suis pas <b>{full_name}</b></strong></a>"
            ),
            person=str(user.person),
            full_name=user.person.get_full_name(),
            logout_url=reverse("disconnect"),
            login_url=reverse("short_code_login"),
        )

    @staticmethod
    def get_already_connected_message(current_user, link_user, link_url):
        return format_html(
            _(
                "Vous êtes actuellement connecté comme <em>{current_person}</em>, mais vous avez suivi un lien qui a été envoyé "
                'à {link_person}. Souhaitez vous <a href="{link_url}"> vous connecter comme {link_person} ?</a>'
            ),
            current_person=str(current_user.person),
            link_person=str(link_user.person),
            link_url=link_url,
        )

    @staticmethod
    def get_already_connected_extra_tags(current_user, link_user, link_url):
        name = (
            link_user.person.first_name
            if link_user.person.first_name
            else link_user.person.display_name
        )
        email = link_user.person.email
        return ",".join(["LOGGED_IN_TO_SOFT_LOGIN_CONNECTION", name, email, link_url])

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not (("p" in request.GET or "_p" in request.GET) and "code" in request.GET):
            return self.get_response(request)

        # preserve other query params than p and code when we redirect
        other_params = request.GET.copy()

        for p in ["p", "_p", "code", "force_login", "from_message"]:
            if p in other_params:
                del other_params[p]

        url = (
            "{}?{}".format(request.path, other_params.urlencode(safe="/"))
            if other_params
            else request.path
        )

        user_pk = request.GET.get("p", request.GET.get("_p"))
        token = request.GET["code"]

        link_user = authenticate(request, user_pk=user_pk, token=token)

        force_login = request.GET.get("force_login")
        no_session = request.GET.get("no_session")
        from_message = request.GET.get("from_message")

        if no_session:
            if link_user:
                request.user = link_user
            return self.get_response(request)
        elif not link_user:
            # if we don't have any link_user, it means the link was forged or expired: we just ignore and redirect to
            # same url without the parameters
            return HttpResponseRedirect(url)
        elif request.user.is_anonymous or force_login:
            # we have a link_user, and current user is anonymous or asked for force_login ==> we log her in and redirect
            login(request, link_user)

            # session var used for external members joining a group or an event
            request.session["login_action"] = datetime.utcnow().timestamp()

            if not from_message:
                messages.add_message(
                    request=request,
                    level=messages.WARNING,
                    message=self.get_just_connected_message(link_user),
                    extra_tags="ANONYMOUS_TO_SOFT_LOGIN_CONNECTION",
                )
        elif request.user != link_user:
            # we have a link_user, but current user is already logged in: we show a warning offering to connect with
            # link_user anyway
            params = request.GET.copy()

            params["force_login"] = "yes"
            link_url = "{}?{}".format(request.path, params.urlencode(safe="/"))

            # Add a `from_message` parameter to avoid falling in the previous condition
            params["from_message"] = "yes"
            extra_tags_link_url = "{}?{}".format(
                request.path, params.urlencode(safe="/")
            )

            messages.add_message(
                request=request,
                level=messages.INFO,
                message=self.get_already_connected_message(
                    request.user, link_user, link_url
                ),
                extra_tags=self.get_already_connected_extra_tags(
                    request.user, link_user, extra_tags_link_url
                ),
            )

        return HttpResponseRedirect(url)
