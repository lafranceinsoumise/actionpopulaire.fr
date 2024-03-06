from uuid import UUID

from django.contrib import messages
from django.db import transaction
from django.http import (
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView, DetailView, RedirectView, FormView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.payments.actions.payments import redirect_to_payment
from agir.payments.models import Payment
from agir.people.actions.subscription import SUBSCRIPTION_TYPE_EXTERNAL
from agir.people.models import PersonFormSubmission
from agir.people.person_forms.display import default_person_form_display
from agir.people.views import ConfirmSubscriptionView
from ..actions.rsvps import (
    rsvp_to_free_event,
    rsvp_to_paid_event_and_create_payment,
    validate_payment_for_rsvp,
    set_guest_number,
    add_free_identified_guest,
    add_paid_identified_guest_and_get_payment,
    validate_payment_for_guest,
    is_participant,
    RSVPException,
    cancel_payment_for_rsvp,
    cancel_payment_for_guest,
    retry_payment_for_rsvp,
    retry_payment_for_guest,
)
from ..forms import BillingForm, GuestsForm, BaseRSVPForm, ExternalRSVPForm
from ..models import Event, RSVP, IdentifiedGuest
from ...people.person_forms.forms import PersonFormController


class RSVPEventView(SoftLoginRequiredMixin, DetailView):
    """RSVP to an event, check one's RSVP, or add guests to your RSVP"""

    model = Event
    template_name = "events/rsvp_event.html"
    default_error_message = _(
        "Il y a eu un problème avec votre inscription. Merci de bien vouloir vérifier si vous n'êtes "
        "pas déjà inscrit⋅e, et retenter si nécessaire."
    )
    context_object_name = "event"

    def get_form(self):
        if self.event.subscription_form is None:
            return None

        kwargs = {
            "instance": None
            if self.user_is_already_rsvped
            else self.request.user.person,
            "is_guest": self.user_is_already_rsvped,
        }

        person = None if self.user_is_already_rsvped else self.request.user.person

        if self.request.method in ("POST", "PUT"):
            kwargs["data"] = self.request.POST

        return PersonFormController(
            is_guest=self.user_is_already_rsvped,
            instance=person,
            base_class=BaseRSVPForm,
            person_form=self.event.subscription_form,
            data=self.request.POST,
            files=self.request.FILES,
        )

    def can_post_form(self):
        person_form = self.event.subscription_form
        person = self.request.user.person

        return not person_form or (
            person_form.is_open and person_form.is_authorized(person)
        )

    def has_form(self):
        if not self.can_post_form():
            return False

        if not self.user_is_already_rsvped:
            return True

        return self.event.allow_guests

    def get_context_data(self, **kwargs):
        if "rsvp" not in kwargs:
            try:
                kwargs["rsvp"] = RSVP.objects.get(
                    event=self.event, person=self.request.user.person
                )
            except RSVP.DoesNotExist:
                pass

        if "is_authorized" not in kwargs:
            kwargs["is_authorized"] = (
                self.event.subscription_form is None
                or self.event.subscription_form.is_authorized(self.request.user.person)
            )

        kwargs = {
            "hide_feedback_button": True,
            "person_form_instance": self.event.subscription_form,
            "event": self.event,
            "is_participant": self.user_is_already_rsvped,
            "submission_data": default_person_form_display.get_formatted_submission(
                kwargs["rsvp"].form_submission
            )
            if "rsvp" in kwargs and kwargs["rsvp"].form_submission
            else None,
            "submission": kwargs["rsvp"].form_submission
            if "rsvp" in kwargs and kwargs["rsvp"].form_submission
            else None,
            "guests": [
                {
                    "pk": guest.pk,
                    "status": guest.get_status_display(),
                    "submission": default_person_form_display.get_formatted_submission(
                        guest.submission
                    )
                    if guest.submission
                    else [],
                    "payment": guest.payment,
                }
                for guest in kwargs["rsvp"].identified_guests.select_related(
                    "submission"
                )
            ]
            if "rsvp" in kwargs
            else None,
            **kwargs,
        }

        if "form" not in kwargs and self.has_form():
            kwargs["form"] = self.get_form()

        return super().get_context_data(**kwargs)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.event = self.object = self.get_object()
        if self.event.subscription_form is None and self.event.is_free:
            return HttpResponseRedirect(reverse("view_event", args=[self.event.pk]))

        context = self.get_context_data(object=self.event)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.event = self.object = self.get_object()

        if not self.event.can_rsvp(request.user.person):
            return HttpResponseRedirect(
                f'{reverse("join")}?type={self.event.for_users}'
            )

        if not self.can_post_form():
            context = self.get_context_data(object=self.event, can_post_form=False)
            return self.render_to_response(context)

        if self.user_is_already_rsvped:
            return self.handle_adding_guests()
        else:
            return self.handle_rsvp()

    def handle_rsvp(self):
        try:
            if not self.event.subscription_form:
                # Without any subscription form, we either simply create the rsvp, or redirect to payment
                if self.event.is_free:
                    # we create the RSVP here for free events
                    rsvp_to_free_event(self.event, self.request.user.person)
                    return self.redirect_to_event(
                        message=_(
                            "Merci de nous avoir signalé votre participation à cet événement."
                        ),
                        level=messages.SUCCESS,
                    )
                else:
                    return self.redirect_to_billing_form()

            form = self.get_form()

            if not form.is_valid():
                context = self.get_context_data(object=self.event, form=form)
                return self.render_to_response(context)

            if form.cleaned_data["is_guest"]:
                self.redirect_to_event(message=self.default_error_message)

            price = 0 if self.event.is_free else self.event.get_price(form.cleaned_data)
            cagnotte = (
                self.event.payment_parameters
                and self.event.payment_parameters.get("cagnotte")
            )

            if price == 0 or cagnotte:
                with transaction.atomic():
                    form.save_submitter()
                    submission = form.save_submission()
                    rsvp_to_free_event(
                        self.event,
                        self.request.user.person,
                        form_submission=submission,
                    )

                    if price != 0:
                        return HttpResponseRedirect(
                            "{}?amount={}".format(
                                reverse(
                                    "cagnottes:personal_information",
                                    kwargs={"slug": cagnotte},
                                ),
                                price,
                            )
                        )
                    return self.redirect_to_rsvp(
                        message=_(
                            "Merci de nous avoir signalé votre participation à cet événenement."
                        ),
                        level=messages.SUCCESS,
                    )
            else:
                form.save_submitter()
                submission = form.save_submission()
                return self.redirect_to_billing_form(submission)
        except RSVPException as e:
            return self.redirect_to_event(message=str(e))

    def handle_adding_guests(self):
        try:
            if not self.event.subscription_form and self.event.is_free:
                guests_form = GuestsForm(self.request.POST)
                if not guests_form.is_valid():
                    return self.redirect_to_event(message=self.default_error_message)

                guests = guests_form.cleaned_data["guests"]

                set_guest_number(self.event, self.request.user.person, guests)
                return self.redirect_to_rsvp(
                    message=_("Merci, votre nombre d'invités a été mis à jour !"),
                    level=messages.SUCCESS,
                )

            if not self.event.subscription_form:
                return self.redirect_to_billing_form(is_guest=True)

            form = self.get_form()

            if not form.is_valid():
                context = self.get_context_data(object=self.event)
                return self.render_to_response(context)

            if not form.cleaned_data["is_guest"]:
                return self.redirect_to_event(message=self.default_error_message)

            if self.event.is_free or self.event.get_price(form.cleaned_data) == 0:
                with transaction.atomic():
                    # do not save the person, only the submission
                    submission = form.save_submission(self.request.user.person)
                    add_free_identified_guest(
                        self.event, self.request.user.person, submission
                    )
                return self.redirect_to_rsvp(
                    message=_("Merci, votre invité a bien été enregistré !"),
                    level=messages.SUCCESS,
                )
            else:
                submission = form.save_submission(self.request.user.person)
                return self.redirect_to_billing_form(submission, is_guest=True)
        except RSVPException as e:
            return self.redirect_to_event(message=str(e))

    def redirect_to_event(self, *, message, level=messages.ERROR):
        if message is not None:
            messages.add_message(request=self.request, level=level, message=message)

        return HttpResponseRedirect(reverse("view_event", args=[self.event.pk]))

    def redirect_to_rsvp(self, *, message, level=messages.ERROR):
        if message is not None:
            messages.add_message(request=self.request, level=level, message=message)

        return HttpResponseRedirect(reverse("rsvp_event", args=[self.event.pk]))

    def redirect_to_billing_form(self, submission=None, is_guest=False):
        if submission:
            self.request.session["rsvp_submission"] = submission.pk
        elif "rsvp_submission" in self.request.session:
            del self.request.session["rsvp_submission"]
        self.request.session["rsvp_event"] = str(self.event.pk)
        self.request.session["is_guest"] = is_guest

        return HttpResponseRedirect(reverse("pay_event"))

    @cached_property
    def user_is_already_rsvped(self):
        return is_participant(self.event, self.request.user.person)


class ChangeRSVPPaymentView(SoftLoginRequiredMixin, DetailView):
    def get_queryset(self):
        return self.request.user.person.rsvps.exclude(payment=None)

    @never_cache
    def get(self, *args, **kwargs):
        rsvp = self.get_object()

        if not rsvp.payment.can_cancel():
            return HttpResponseNotFound()

        if rsvp.form_submission:
            self.request.session["rsvp_submission"] = rsvp.form_submission.pk
        elif "rsvp_submission" in self.request.session:
            del self.request.session["rsvp_submission"]
        self.request.session["rsvp_event"] = str(rsvp.event.pk)
        self.request.session["is_guest"] = False

        return HttpResponseRedirect(reverse("pay_event"))


class ChangeIdentifiedGuestPaymentView(SoftLoginRequiredMixin, DetailView):
    def get_queryset(self):
        return IdentifiedGuest.objects.filter(
            rsvp__person=self.request.user.person
        ).exclude(payment=None)

    @never_cache
    def get(self, *args, **kwargs):
        guest = self.get_object()

        if not guest.payment.can_cancel():
            return HttpResponseNotFound()

        if guest.submission:
            self.request.session["rsvp_submission"] = guest.submission.pk
        elif "rsvp_submission" in self.request.session:
            del self.request.session["rsvp_submission"]
        self.request.session["rsvp_event"] = str(guest.rsvp.event.pk)
        self.request.session["is_guest"] = True

        return HttpResponseRedirect(reverse("pay_event"))


@method_decorator(never_cache, name="get")
class PayEventView(SoftLoginRequiredMixin, UpdateView):
    """View for the billing form for paid events"""

    form_class = BillingForm
    template_name = "events/pay_event.html"
    generic_error_message = _(
        "Il y a eu un problème avec votre paiement. Merci de réessayer plus tard"
    )

    def get_object(self, queryset=None):
        return self.request.user.person

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                "event": self.event,
                "submission": self.submission,
                "price": self.event.get_price(self.submission and self.submission.data)
                / 100,
                "submission_data": default_person_form_display.get_formatted_submission(
                    self.submission
                )
                if self.submission
                else None,
            }
        )
        return super().get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        submission_pk = self.request.session.get("rsvp_submission")
        event_pk = self.request.session.get("rsvp_event")

        if not event_pk:
            return HttpResponseBadRequest("no event")

        try:
            event_pk = UUID(event_pk)
        except ValueError:
            return HttpResponseBadRequest("no event")

        try:
            self.event = Event.objects.upcoming().get(pk=event_pk)
        except Event.DoesNotExist:
            return HttpResponseBadRequest("no event")

        if self.event.subscription_form:
            if not submission_pk:
                return self.display_error_message(self.generic_error_message)

            try:
                self.submission = PersonFormSubmission.objects.get(pk=submission_pk)
            except PersonFormSubmission.DoesNotExist:
                return self.display_error_message(self.generic_error_message)

            if self.submission.form != self.event.subscription_form:
                return self.display_error_message(self.generic_error_message)
        else:
            self.submission = None

        self.is_guest = self.request.session.get("is_guest", False)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["submission"] = self.submission
        kwargs["event"] = self.event
        kwargs["is_guest"] = self.is_guest
        return kwargs

    def form_valid(self, form):
        event = form.cleaned_data["event"]
        person = self.request.user.person
        submission = form.cleaned_data["submission"]
        is_guest = form.cleaned_data["is_guest"]
        payment_mode = form.cleaned_data["payment_mode"]

        if not is_guest:
            # we save the billing information only if the person is paying for herself or himself
            form.save()

        with transaction.atomic():
            try:
                if is_guest:
                    payment = add_paid_identified_guest_and_get_payment(
                        event, person, payment_mode, submission
                    )
                else:
                    payment = rsvp_to_paid_event_and_create_payment(
                        event, person, payment_mode, submission
                    )

            except RSVPException as e:
                return self.display_error_message(str(e))

        return redirect_to_payment(payment)

    def display_error_message(self, message, level=messages.ERROR):
        messages.add_message(request=self.request, message=message, level=level)

        return HttpResponseRedirect(reverse("view_event", args=[self.event.pk]))


class EventPaidView(RedirectView):
    """View shown when the event has been paid"""

    def get_redirect_url(self, *args, **kwargs):
        payment = self.kwargs["payment"]
        event = Event.objects.get(pk=self.kwargs["payment"].meta["event_id"])

        if url := event.meta.get("payment_success_url"):
            return url

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message=f"Votre inscription {payment.get_price_display()} pour l'événement « {event.name} » a bien été enregistré. "
            f"Votre inscription sera confirmée dès validation du paiement.",
        )
        return reverse("rsvp_event", args=[self.kwargs["payment"].meta["event_id"]])


def notification_listener(payment):
    if payment.meta.get("VERSION") == "2":
        # VERSION 2
        is_guest = payment.meta["is_guest"]

        if payment.status == Payment.STATUS_COMPLETED:
            # we don't check for cancellation of the event because we want all actually paid rsvps to be registered in
            # case we need to manage refunding

            # RSVP or IdentifiedGuest model has already been created, only need to confirm it
            if is_guest:
                return validate_payment_for_guest(payment)

            return validate_payment_for_rsvp(payment)

        if payment.status in (Payment.STATUS_CANCELED, Payment.STATUS_REFUND):
            cancel_payment_for_rsvp(payment)
            cancel_payment_for_guest(payment)
            return

        if payment.status == Payment.STATUS_WAITING:
            retry_payment_for_rsvp(payment)
            retry_payment_for_guest(payment)
            return

    else:
        # should not happen anymore
        pass


class ExternalRSVPView(ConfirmSubscriptionView, FormView, DetailView):
    queryset = Event.objects.filter(subtype__allow_external=True)
    form_class = ExternalRSVPForm
    show_already_created_message = False
    default_type = SUBSCRIPTION_TYPE_EXTERNAL

    def dispatch(self, request, *args, **kwargs):
        self.event = self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def success_page(self, params):
        if RSVP.objects.filter(person=self.person, event=self.event).exists():
            messages.add_message(
                request=self.request,
                level=messages.INFO,
                message=_("Vous êtes déjà inscrit⋅e à l'événement."),
            )
            return HttpResponseRedirect(reverse("view_event", args=[self.event.pk]))

        if self.event.is_free and not self.event.subscription_form:
            RSVP.objects.get_or_create(person=self.person, event=self.event)
            messages.add_message(
                request=self.request,
                level=messages.INFO,
                message=_("Vous avez bien été inscrit⋅e à l'événement."),
            )

        return HttpResponseRedirect(reverse("view_event", args=[self.event.pk]))

    def form_valid(self, form):
        form.send_confirmation_email(self.event)
        messages.add_message(
            request=self.request,
            level=messages.INFO,
            message=_(
                "Un email vous a été envoyé. Afin de confirmer votre participation, merci de cliquer sur le "
                "lien qu'il contient."
            ),
        )
        return HttpResponseRedirect(reverse("view_event", args=[self.event.pk]))

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse("view_event", args=[self.event.pk]))
