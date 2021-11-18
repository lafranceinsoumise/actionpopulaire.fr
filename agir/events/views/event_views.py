import locale
import os
import textwrap

import ics
import pytz
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import (
    Http404,
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseGone,
)
from django.template import loader
from django.template.backends.django import DjangoTemplates
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import ugettext as _, ngettext
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import (
    UpdateView,
    DeleteView,
    DetailView,
    RedirectView,
    CreateView,
)
from django.views.generic.detail import SingleObjectMixin
from rest_framework import status

from agir.activity.models import Activity
from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    GlobalOrObjectPermissionRequiredMixin,
    SoftLoginRequiredMixin,
)
from agir.events.actions.rsvps import assign_jitsi_meeting
from agir.front.view_mixins import (
    ChangeLocationBaseView,
    FilterView,
)
from agir.lib.tasks import create_static_map_image_from_coordinates
from ..filters import EventFilter
from ..forms import (
    EventGeocodingForm,
    EventLegalForm,
    UploadEventImageForm,
    AuthorForm,
)
from ..models import Event, RSVP, Invitation, OrganizerConfig
from ..tasks import (
    send_event_report,
    send_secretariat_notification,
    send_accepted_group_coorganization_invitation_notification,
    send_refused_group_coorganization_invitation_notification,
)
from ...api import settings
from ...carte.models import StaticMapImage

__all__ = [
    "ManageEventView",
    "ModifyEventView",
    "QuitEventView",
    "EventParticipationView",
    "EventIcsView",
    "ChangeEventLocationView",
    "EditEventReportView",
    "SendEventReportView",
    "EditEventLegalView",
    "UploadEventImageView",
    "EventSearchView",
    "EventDetailMixin",
    "EventOGImageView",
    "AcceptEventCoorganizationInvitationView",
    "RefuseEventCoorganizationInvitationView",
]


# PUBLIC VIEWS
# ============


class EventOGImageView(DetailView):
    model = Event
    event = None
    static_root = os.path.join(
        settings.BASE_DIR, "front", "static", "front", "og-image"
    )

    def get_date_string(self):
        # set locale for displaying day name in french
        locale.setlocale(locale.LC_ALL, "fr_FR.utf8")

        if settings.TIME_ZONE == self.event.timezone:
            return self.event.start_time.strftime(f"%A %d %B À %-H:%M").capitalize()

        return (
            self.event.start_time.astimezone(pytz.timezone(self.event.timezone))
            .strftime(f"%A %d %B À %-H:%M %Z")
            .capitalize()
        )

    def get_location_string(self):
        if self.event.location_city and self.event.location_zip:
            return f"{self.event.location_city} ({self.event.location_zip})"
        if self.event.location_city:
            return self.event.location_city
        if self.event.location_zip:
            return self.event.location_zip

        return ""

    def get_illustration(self):
        if self.event.coordinates is None:
            return self.get_image_from_file("Frame-193.png")

        static_map_image = StaticMapImage.objects.filter(
            center__distance_lt=(
                self.event.coordinates,
                StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE,
            ),
        ).first()

        if static_map_image is None:
            create_static_map_image_from_coordinates.delay(
                [self.event.coordinates[0], self.event.coordinates[1]]
            )
            return self.get_image_from_file("Frame-193.png")

        static_map_image.image.open()
        map = ImageOps.fit(Image.open(static_map_image.image), (1200, 278))

        # Add marker to static map image
        icon = self.get_image_from_file("map-marker.png")
        icon = icon.resize((116, 139), Image.ANTIALIAS)
        map.paste(icon, (542, 49), icon)

        return map

    def get_font(self, size, bold=False):
        filename = (
            os.path.join(self.static_root, "poppins-bold.ttf")
            if bold
            else os.path.join(self.static_root, "Poppins-Medium.ttf")
        )
        return ImageFont.truetype(
            filename, size=size, encoding="utf-8", layout_engine=ImageFont.LAYOUT_BASIC,
        )

    def get_image_from_file(self, filename):
        return Image.open(os.path.join(self.static_root, filename))

    def generate_thumbnail(self):
        image = Image.new("RGB", (1200, 630), "#FFFFFF")
        draw = ImageDraw.Draw(image)

        # Draw illustration image
        illustration = self.get_illustration()
        image.paste(illustration, (0, 0), illustration)

        # Draw event location and date
        # ex: Paris (75010) - Mercredi 7 Juillet à 19:00
        draw.text(
            (108, 315),
            f"{self.get_location_string()} – {self.get_date_string()}",
            fill=(63, 38, 130, 0),
            align="left",
            font=self.get_font(32, bold=True),
        )

        # Draw event name
        lines = textwrap.wrap(
            self.event.name.capitalize(), width=36, max_lines=2, placeholder="…"
        )
        font = self.get_font(45 if len(lines) > 1 else 56)
        y = 369
        for line in lines:
            draw.text((108, y), line, font=font, fill=(0, 0, 0, 0), align="left")
            y += 63

        # Draw Action Populaire logo
        image.paste(self.get_image_from_file("bande-ap.png"), (0, 535))

        # Draw Union Populaire logo
        logo_up = self.get_image_from_file("UP+JLM.png")
        image.paste(logo_up, (1200 - 453 - 100, 630 - 186), logo_up)

        return image

    def get(self, request, *args, **kwargs):
        self.event = self.get_object()
        image = self.generate_thumbnail()
        response = HttpResponse(content_type="image/png")
        image.save(response, "PNG")
        return response


class EventSearchView(FilterView):
    """Vue pour lister les événements et les rechercher
    """

    template_name = "events/event_search.html"
    context_object_name = "events"
    success_url = reverse_lazy("search_event")
    paginate_by = 20
    queryset = Event.objects.filter(
        visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
    )
    filter_class = EventFilter


class EventContextMixin:
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            rsvp=self.request.user.is_authenticated
            and self.object.rsvps.filter(person=self.request.user.person).first(),
            is_organizer=self.request.user.is_authenticated
            and self.object.organizers.filter(pk=self.request.user.person.id).exists(),
            organizers_groups=self.object.organizers_groups.distinct(),
            event_images=self.object.images.all(),
            **kwargs,
        )


class EventDetailMixin(GlobalOrObjectPermissionRequiredMixin):
    permission_required = ("events.view_event",)
    queryset = Event.objects.all()

    def handle_no_permission(self):
        if self.get_object().visibility == Event.VISIBILITY_ADMIN:
            return HttpResponseGone()
        return redirect_to_login(self.request.get_full_path())


class EventParticipationView(
    SoftLoginRequiredMixin, EventContextMixin, EventDetailMixin, DetailView
):
    template_name = "events/participation.html"
    permission_required = ("events.view_event", "events.participate_online")
    permission_denied_message = _(
        "Vous devez être inscrit⋅e à l'événement pour accéder à cette page."
    )
    custom_template_engine = DjangoTemplates(
        {
            "APP_DIRS": False,
            "DIRS": [],
            "NAME": "ParticipationEngine",
            "OPTIONS": {"builtins": []},
        }
    )

    def get_context_data(self, **kwargs):
        if self.object.is_past():
            raise PermissionDenied("L'événement est terminé !")
        if not self.object.is_current():
            raise PermissionDenied("L'événement n'est pas encore commencé !")

        context_data = super().get_context_data(**kwargs)

        if context_data["rsvp"].jitsi_meeting is None:
            assign_jitsi_meeting(context_data["rsvp"])

        jitsi_fragment = loader.get_template("events/jitsi_fragment.html").render(
            {"jitsi_meeting": context_data["rsvp"].jitsi_meeting}
        )

        if self.object.participation_template:
            template = self.custom_template_engine.from_string(
                self.object.participation_template
            )
            context_data["content"] = template.render(
                {
                    "jitsi_video": jitsi_fragment,
                    "group_code": context_data["rsvp"].jitsi_meeting.room_name,
                }
            )
        else:
            context_data["content"] = jitsi_fragment

        return context_data


@method_decorator(never_cache, name="get")
class QuitEventView(
    SoftLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, DeleteView
):
    template_name = "events/quit.html"
    permission_required = ("events.delete_rsvp",)
    success_url = reverse_lazy("dashboard")
    context_object_name = "rsvp"

    def get_queryset(self):
        return RSVP.objects.filter(event__end_time__gte=timezone.now())

    def get_object(self, queryset=None):
        try:
            rsvp = (
                self.get_queryset()
                .select_related("event")
                .get(event__pk=self.kwargs["pk"], person=self.request.user.person)
            )
            if not self.request.user.has_perm("events.view_event", rsvp.event):
                raise Http404
        except RSVP.DoesNotExist:
            raise Http404()

        return rsvp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.object.event
        context["success_url"] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        # first get response to make sure there's no error before adding message
        res = super().delete(request, *args, **kwargs)

        messages.add_message(
            request,
            messages.SUCCESS,
            format_html(
                _("Vous ne participez plus à l'événement <em>{}</em>"),
                self.object.event.name,
            ),
        )

        return res


@method_decorator(never_cache, name="get")
class UploadEventImageView(
    SoftLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, CreateView
):
    template_name = "events/upload_event_image.html"
    form_class = UploadEventImageForm
    permission_required = ("events.upload_image",)
    permission_denied_to_not_found = True

    def get_queryset(self):
        return Event.objects.public().past(as_of=timezone.now())

    def get_success_url(self):
        return reverse("view_event", args=(self.event.pk,))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"author": self.request.user.person, "event": self.event})
        return kwargs

    def get_author_form(self):
        author_form_kwargs = {"instance": self.request.user.person}
        if self.request.method in ["POST", "PUT"]:
            author_form_kwargs["data"] = self.request.POST

        return AuthorForm(**author_form_kwargs)

    def get_context_data(self, **kwargs):
        if "author_form" not in kwargs:
            kwargs["author_form"] = self.get_author_form()

        return super().get_context_data(event=self.event, **kwargs)

    def get_permission_object(self):
        return self.event

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.event = self.get_object()
        except Event.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        if not self.has_permission():
            raise PermissionDenied(
                _("Seuls les participants à l'événement peuvent poster des images")
            )

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        author_form = self.get_author_form()

        if form.is_valid() and author_form.is_valid():
            return self.form_valid(form, author_form)
        else:
            return self.form_invalid(form, author_form)

    # noinspection PyMethodOverriding
    def form_invalid(self, form, author_form):
        return self.render_to_response(
            self.get_context_data(form=form, author_form=author_form)
        )

    # noinspection PyMethodOverriding
    def form_valid(self, form, author_form):
        author_form.save()
        form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Votre photo a correctement été importée, merci de l'avoir partagée !"),
        )

        return HttpResponseRedirect(self.get_success_url())


class EventIcsView(EventDetailMixin, DetailView):
    model = Event

    def render_to_response(self, context, **response_kwargs):
        ics_calendar = ics.Calendar(events=[context["event"].to_ics()])

        return HttpResponse(ics_calendar, content_type="text/calendar")


# ADMIN VIEWS


class BaseEventAdminView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, View
):
    permission_required = ("events.change_event",)
    queryset = Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)


@method_decorator(never_cache, name="get")
class ManageEventView(RedirectView):
    permanent = True
    pattern_name = "view_event_settings"
    query_string = True


@method_decorator(never_cache, name="get")
class ModifyEventView(RedirectView):
    permanent = True
    pattern_name = "view_event_settings_general"
    query_string = True


@method_decorator(never_cache, name="get")
class EditEventReportView(RedirectView,):
    permanent = True
    pattern_name = "view_event_settings_feedback"
    query_string = True


@method_decorator(never_cache, name="get")
class ChangeEventLocationView(
    BaseEventAdminView, ChangeLocationBaseView,
):
    template_name = "events/change_location.html"
    form_class = EventGeocodingForm
    success_view_name = "manage_event"

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now(), published_only=False)


@method_decorator(never_cache, name="get")
class AcceptEventCoorganizationInvitationView(
    HardLoginRequiredMixin,
    GlobalOrObjectPermissionRequiredMixin,
    SingleObjectMixin,
    View,
):
    permission_required = ("events.respond_to_coorganization_invitation",)
    target_status = Invitation.STATUS_ACCEPTED
    queryset = Invitation.objects.exclude(
        event__visibility=Event.VISIBILITY_ADMIN
    ).exclude(group__published=False)

    def post_save(self, invitation):
        # Delete the invitation activity
        (
            Activity.objects.filter(
                event=invitation.event,
                supportgroup=invitation.group,
                type=Activity.TYPE_GROUP_COORGANIZATION_INVITE,
            ).delete()
        )

        current_organizer_ids = list(
            invitation.event.organizers.all().values_list("id", flat=True)
        )

        # Create a new organizer config object if none exists
        (_, created) = OrganizerConfig.objects.get_or_create(
            event=invitation.event,
            as_group=invitation.group,
            defaults={"person": self.request.user.person, "is_creator": False},
        )

        if created:
            # Notify the event organizers
            send_accepted_group_coorganization_invitation_notification.delay(
                invitation.id, current_organizer_ids
            )
            # Add a success flash message
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Votre groupe est maintenant coorganisateur de l'événement",
            )
        else:
            messages.add_message(
                self.request,
                messages.INFO,
                "Votre groupe est déjà coorganisateur de l'événement",
            )

    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.ERROR,
            "Le lien d'invitation n'est pas ou plus valide.",
        )
        return HttpResponseRedirect(reverse("dashboard"))

    def get(self, request, pk, *args, **kwargs):
        try:
            invitation = self.get_queryset().get(pk=pk)
        except Invitation.DoesNotExist:
            return self.handle_no_permission()

        with transaction.atomic():
            invitation.status = self.target_status
            invitation.person_recipient = self.request.user.person
            invitation.save()
            self.post_save(invitation)

            return HttpResponseRedirect(
                reverse("view_event", kwargs={"pk": invitation.event.pk})
            )


@method_decorator(never_cache, name="get")
class RefuseEventCoorganizationInvitationView(AcceptEventCoorganizationInvitationView):
    permission_required = ("events.respond_to_coorganization_invitation",)
    target_status = Invitation.STATUS_REFUSED

    def get_queryset(self):
        # Only allow refusing pending invitations
        return self.queryset.filter(status=Invitation.STATUS_PENDING)

    def post_save(self, invitation):
        # Notify the event organizers
        current_organizer_ids = list(
            invitation.event.organizers.all().values_list("id", flat=True)
        )
        send_refused_group_coorganization_invitation_notification.delay(
            invitation.id, current_organizer_ids
        )
        # Add a success flash message
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "L'invitation a coorganiser l'événement a été refusée",
        )


class SendEventReportView(
    BaseEventAdminView, SingleObjectMixin, View,
):
    model = Event

    def post(self, request, pk, *args, **kwargs):
        event = self.get_object()
        if not event.report_summary_sent and event.is_past() and event.report_content:
            send_event_report.delay(event.pk)
            participants = event.participants
            messages.add_message(
                self.request,
                messages.SUCCESS,
                ngettext(
                    "Votre mail a correctement été envoyé à {participants} participant⋅e.",
                    "Votre mail a correctement été envoyé à {participants} participant⋅e⋅s.",
                    participants,
                ).format(participants=participants),
            )
            request.session["report_sent"] = str(event.pk)
        return HttpResponseRedirect(reverse("manage_event", kwargs={"pk": pk}))


@method_decorator(never_cache, name="get")
class EditEventLegalView(BaseEventAdminView, UpdateView):
    template_name = "events/edit_legal.html"
    form_class = EventLegalForm
    model = Event

    def form_valid(self, form):
        result = super().form_valid(form)

        if len(list(form.incomplete_sections)) == 0:
            message = (
                "Les informations légales sont complètes. Le secrétariat général de la campagne en a été "
                "averti, votre demande sera examinée dans les plus brefs délais."
            )
            send_secretariat_notification.delay(
                self.object.pk, self.request.user.person.pk
            )
        else:
            message = "Les informations légales ont bien été mises à jour."
        messages.add_message(self.request, messages.SUCCESS, message)

        return result

    def get_success_url(self):
        return reverse("manage_event", args=(self.object.pk,))
