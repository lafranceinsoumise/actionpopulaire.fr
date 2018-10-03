from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, RedirectView
from django.contrib.auth import login, logout, REDIRECT_FIELD_NAME
from django.utils.http import is_safe_url, urlquote

from agir.people.models import Person
from .forms import EmailForm, CodeForm


def valid_emails(candidate_emails):
    for email in candidate_emails:
        try:
            validate_email(email)
            yield email
        except ValidationError:
            pass


def get_bookmarked_emails(request):
    if 'knownEmails' not in request.COOKIES:
        return []
    candidate_emails = request.COOKIES.get('knownEmails').split(',')
    return list(valid_emails(candidate_emails))


def bookmark_email(email, request, response):
    domain = '.'.join(request.META.get('HTTP_HOST', '').split('.')[-2:])

    emails = get_bookmarked_emails(request)

    if email in emails:
        emails.remove(email)

    emails.insert(0, email)

    response.set_cookie('knownEmails', value=','.join(emails[0:4]), max_age=365, domain=domain, secure=True,
                        httponly=True)

    return response


class RedirectToMixin():
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''


class SendEmailView(RedirectToMixin, FormView):
    form_class = EmailForm
    template_name = "authentication/send_email.html"

    def form_valid(self, form):
        if not form.send_email():
            return self.form_invalid(form)

        redirect_to = self.get_redirect_url()
        success_url = reverse('check_short_code', kwargs={'user_pk': form.person.pk})

        local_expiration_time = timezone.localtime(form.expiration).strftime('%H:%M')

        messages.add_message(
            self.request,
            messages.DEBUG,
            f"Le code de connexion est {form.short_code} (expiration à {local_expiration_time})."
        )

        if redirect_to:
            success_url += f"?{self.redirect_field_name}={urlquote(redirect_to)}"

        return bookmark_email(
            form.cleaned_data['email'],
            self.request,
            HttpResponseRedirect(success_url)
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            bookmarked_emails=get_bookmarked_emails(self.request),
            **kwargs
        )


class CheckCodeView(RedirectToMixin, FormView):
    form_class = CodeForm
    template_name = "authentication/check_short_code.html"
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        try:
            self.person = Person.objects.get(pk=self.kwargs['user_pk'])
            return super().dispatch(request, *args, **kwargs)
        except Person.DoesNotExist:
            return HttpResponseRedirect(reverse('short_code_login'))

    def get_success_url(self):
        return self.get_redirect_url() or '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['person'] = self.person
        return kwargs

    def form_valid(self, form):
        login(self.request, form.role)

        return super().form_valid(form)


class DisconnectView(RedirectView):
    url = settings.MAIN_DOMAIN

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url() or self.url
