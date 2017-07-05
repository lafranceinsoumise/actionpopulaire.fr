from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, RedirectView
from django.core.urlresolvers import reverse_lazy, reverse
from django.conf import settings
from django.utils.http import is_safe_url
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout

from requests_oauthlib import OAuth2Session

from people.models import Person
from events.models import Event, Calendar

from .forms import SimpleSubscriptionForm, OverseasSubscriptionForm, EventForm
from .view_mixins import SuccessMessageView, LoginRequiredMixin


class SubscriptionSuccessView(SuccessMessageView):
    title = "Merci de votre appui"
    message = """
    Votre soutien est bien enregistré. Vous serez tenu au courant de l'actualité du mouvement.
    """


class SimpleSubscriptionView(CreateView):
    template_name = "front/simple_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = SimpleSubscriptionForm


class OverseasSubscriptionView(CreateView):
    template_name = "front/overseas_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = OverseasSubscriptionForm


class CreateEventView(LoginRequiredMixin, CreateView):
    template_name = "front/event_form.html"
    success_url = reverse_lazy("create_event_success")
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Publiez votre événement')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendar'] = Calendar.objects.get(label='evenements_locaux')
        return kwargs


class UpdateEventView(LoginRequiredMixin, UpdateView):
    template_name = "front/event_form.html"
    success_url = reverse_lazy("update_event_success")
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Modifiez votre événement')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendar'] = self.object.calendar
        return kwargs


class CreateEventSuccessView(SuccessMessageView):
    title = "Votre événement a bien été créé"
    message = """
    Vous allez recevoir un mail vous permettant d'administrer votre nouvel événement.
    """


class UpdateEventSuccessView(SuccessMessageView):
    title = "Votre événement a été mis à jour"
    message = """
    Vous allez recevoir un mail vous permettant d'administrer votre nouvel événement.
    """


class OauthRedirectView(RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, *args, **kwargs):
        client = OAuth2Session(
            client_id=settings.OAUTH['client_id'],
            redirect_uri=settings.OAUTH['redirect_domain'] + reverse('oauth_return_view'),
            scope=['view_profile'],
        )

        # extract next url
        next_url = self.request.GET.get('next', None)

        # save it to the session
        if next_url and is_safe_url(next_url):
            self.request.session['login_next_url'] = next_url

        # the user is then redirected to the auth provider with the right parameters
        url, state = client.authorization_url(settings.OAUTH['authorization_url'])

        # the nonce is saved inside the session
        self.request.session['oauth2_nonce'] = state
        return url


class OauthReturnView(RedirectView):
    http_method_names = ['get']
    default_url = reverse_lazy('login_success')

    def get(self, request, *args, **kwargs):
        state_nonce = request.session.get('oauth2_nonce', None)

        if state_nonce is None:
            return HttpResponseBadRequest(b'bad state')

        client = OAuth2Session(
            client_id=settings.OAUTH['client_id'],
            redirect_uri=settings.OAUTH['redirect_domain'] + reverse('oauth_return_view'),
            scope=['view_profile'],
            state=state_nonce,
        )

        token = client.fetch_token(
            token_url=settings.OAUTH['token_exchange_url'],
            authorization_response=self.request.build_absolute_uri(),
            client_id=settings.FRONT_OAUTH_CLIENT, client_secret=settings.FRONT_OAUTH_SECRET
        )

        if 'profile' not in token:
            return HttpResponseBadRequest('No `profile` key returned by Oauth server')

        profile_url = token['profile']

        user = authenticate(profile_url=profile_url)

        if user:
            login(request, user)
        else:
            return HttpResponseBadRequest('No corresponding user')

        del request.session['oauth2_nonce']

        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        next_url = self.request.session.get('login_next_url', None)

        if next_url and is_safe_url(next_url):
            return next_url

        return self.default_url


class LogOffView(RedirectView):
    url = settings.OAUTH['logoff_url']

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
