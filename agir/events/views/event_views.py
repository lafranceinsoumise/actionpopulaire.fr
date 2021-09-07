import locale
import os

import ics
import pytz
from PIL import Image, ImageDraw, ImageFont
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
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
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.views.generic.detail import SingleObjectMixin
from rest_framework import status

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
from agir.lib.views import ImageSizeWarningMixin
from ..filters import EventFilter
from ..forms import (
    EventForm,
    AddOrganizerForm,
    EventGeocodingForm,
    EventReportForm,
    UploadEventImageForm,
    AuthorForm,
    EventLegalForm,
)
from ..models import Event, RSVP
from ..tasks import (
    send_cancellation_notification,
    send_event_report,
    send_secretariat_notification,
)
from ...api import settings
from ...carte.models import StaticMapImage

__all__ = [
    "ManageEventView",
    "ModifyEventView",
    "QuitEventView",
    "CancelEventView",
    "EventParticipationView",
    "EventIcsView",
    "ChangeEventLocationView",
    "EditEventReportView",
    "SendEventReportView",
    "EditEventLegalView",
    "UploadEventImageView",
    "EventSearchView",
    "EventDetailMixin",
    "EventThumbnailView",
]


# PUBLIC VIEWS
# ============


class EventThumbnailView(DetailView):
    model = Event
    event = None
    static_root = os.path.join(
        settings.BASE_DIR, "front", "static", "front", "og-image"
    )

    def get(self, request, *args, **kwargs):
        self.event = self.get_object()
        image = self.generate_thumbnail()
        response = HttpResponse(content_type="image/png")
        image.save(response, "PNG")
        return response

    def generate_thumbnail(self):
        image = Image.new("RGB", (int(1200), int(630)), "#FFFFFF")
        draw = ImageDraw.Draw(image)

        if self.event.coordinates is None:
            illustration = Image.open(os.path.join(self.static_root, "Frame-193.png"))
            image.paste(illustration, (0, 0), illustration)
        else:
            static_map_image = StaticMapImage.objects.filter(
                center__distance_lt=(
                    self.event.coordinates,
                    StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE,
                ),
            ).first()

            if static_map_image is not None:
                static_map_image.image.open()
                illustration = Image.open(static_map_image.image)
                illustration = illustration.resize(
                    (1200, round(illustration.height * (1200 / illustration.width))),
                    Image.ANTIALIAS,
                )
                crop_w = (illustration.width - 1200) / 2
                crop_h = (illustration.height - 278) / 2
                illustration = illustration.crop(
                    (crop_w, crop_h, crop_w + 1200, crop_h + 278)
                )
                image.paste(illustration, (0, 0), illustration)
                icon = Image.open(os.path.join(self.static_root, "map-marker.png"))
                icon = icon.resize((50, 65), Image.ANTIALIAS)
                image.paste(icon, (575, 75), icon)
            else:
                illustration = Image.open(
                    os.path.join(self.static_root, "Frame-193.png")
                )

        font_bold = ImageFont.truetype(
            os.path.join(self.static_root, "poppins-bold.ttf"),
            size=27,
            encoding="utf-8",
            layout_engine=ImageFont.LAYOUT_BASIC,
        )

        # set locale for displaying day name in french
        locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
        date = (
            self.event.start_time.astimezone(pytz.timezone(self.event.timezone))
            .strftime(
                f"%A %d %B À %-H:%M{' %Z' if self.event.timezone != settings.TIME_ZONE else ''}"
            )
            .capitalize()
        )

        if len(self.event.name) < 30:
            draw.text(
                (108, 350),
                self.event.location_city.upper()
                + " ("
                + self.event.location_zip
                + ") — "
                + date.upper(),
                fill=(87, 26, 255, 0),
                align="left",
                font=font_bold,
            )

            draw.text(
                (108, 400),
                self.event.name.capitalize(),
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(56),
            )
        elif len(self.event.name) < 36:
            draw.text(
                (108, 319),
                self.event.location_city.upper()
                + " ("
                + self.event.location_zip
                + ") — "
                + date.upper(),
                fill=(87, 26, 255, 0),
                align="left",
                font=font_bold,
            )

            draw.text(
                (108, 369),
                self.event.name.capitalize(),
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )
        elif len(self.event.name) < 74:
            draw.text(
                (108, 319),
                self.event.location_city.upper()
                + " ("
                + self.event.location_zip
                + ") — "
                + date.upper(),
                fill=(87, 26, 255, 0),
                align="left",
                font=font_bold,
            )

            draw.text(
                (108, 369),
                self.event.name[0:36].capitalize(),
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )
            draw.text(
                (108, 430),
                self.event.name[37:73],
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )
        else:
            draw.text(
                (108, 319),
                self.event.location_city.upper()
                + " ("
                + self.event.location_zip
                + ") — "
                + date.upper(),
                fill=(87, 26, 255, 0),
                align="left",
                font=font_bold,
            )

            draw.text(
                (108, 369),
                self.event.name[0:36].capitalize(),
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )
            draw.text(
                (108, 430),
                self.event.name[37:73] + "...",
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )

        logo_ap = Image.open(os.path.join(self.static_root, "bande-ap.png"))
        logo_ap = logo_ap.resize((1200, 95), Image.ANTIALIAS)
        image.paste(logo_ap, (0, 535), logo_ap)

        return image

    def get_image_font(self, size):
        return ImageFont.truetype(
            os.path.join(self.static_root, "Poppins-Medium.ttf"),
            size=size,
            encoding="utf-8",
            layout_engine=ImageFont.LAYOUT_BASIC,
        )


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
    meta_description = "Participez et organisez des événements pour soutenir la candidature de Jean-Luc Mélenchon pour 2022"
    queryset = Event.objects.all()
    bundle_name = "front/app"
    data_script_id = "exportedEvent"

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
    permission_required = ("events.view_event",)
    permission_denied_to_not_found = True

    def get_queryset(self):
        return Event.objects.past(as_of=timezone.now())

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
            self.event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None
        if not self.event.rsvps.filter(person=request.user.person).exists():
            raise PermissionDenied(
                _("Seuls les participants à l'événement peuvent poster des images")
            )

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        if not self.event.rsvps.filter(person=request.user.person).exists():
            raise PermissionDenied(
                _("Seuls les participants à l'événement peuvent poster des images")
            )

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
class ManageEventView(BaseEventAdminView, DetailView):
    template_name = "events/manage.html"

    error_messages = {
        "denied": _(
            "Vous ne pouvez pas accéder à cette page sans être organisateur de l'événement."
        )
    }

    def get_success_url(self):
        return reverse("manage_event", kwargs={"pk": self.object.pk})

    def get_form(self):
        kwargs = {}

        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST})

        return AddOrganizerForm(self.object, **kwargs)

    def get_context_data(self, **kwargs):
        if "add_organizer_form" not in kwargs:
            kwargs["add_organizer_form"] = self.get_form()

        try:
            report_is_sent = self.request.session["report_sent"] == str(self.object.pk)
            del self.request.session["report_sent"]
        except KeyError:
            report_is_sent = False

        legal_form = EventLegalForm(self.object)

        return super().get_context_data(
            report_is_sent=report_is_sent,
            organizers=self.object.organizers.all(),
            organizing_groups=self.object.organizers_groups.all().distinct(),
            rsvps=self.object.rsvps.all(),
            legal_sections=legal_form.included_sections,
            incomplete_sections=list(legal_form.incomplete_sections),
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_past():
            raise PermissionDenied(
                _("Vous ne pouvez pas ajouter d'organisateur à un événement terminé.")
            )

        form = self.get_form()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(add_organizer_form=form))


@method_decorator(never_cache, name="get")
class ModifyEventView(ImageSizeWarningMixin, BaseEventAdminView, UpdateView):
    template_name = "events/modify.html"
    form_class = EventForm
    image_field = "image"

    def get_success_url(self):
        return reverse("manage_event", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now(), published_only=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["person"] = self.request.user.person
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Modifiez votre événement")
        return context

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message=format_html(
                _("Les modifications de l'événement <em>{}</em> ont été enregistrées."),
                self.object.name,
            ),
        )

        return res


@method_decorator(never_cache, name="get")
class CancelEventView(BaseEventAdminView, DetailView):
    template_name = "events/cancel.html"
    success_url = reverse_lazy("list_events")

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now(), published_only=False)

    def post(self, request, *args, **kwargs):
        self.object = self.event = self.get_object()

        self.event.visibility = Event.VISIBILITY_ADMIN
        self.event.save()

        send_cancellation_notification.delay(self.object.pk)

        messages.add_message(
            request,
            messages.WARNING,
            _("L'événement « {} » a bien été annulé.").format(self.object.name),
        )

        return HttpResponseRedirect(self.success_url)


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
class EditEventReportView(
    BaseEventAdminView, ImageSizeWarningMixin, UpdateView,
):
    template_name = "events/edit_event_report.html"
    form_class = EventReportForm
    image_field = "report_image"

    def get_success_url(self):
        return reverse("manage_event", args=(self.object.pk,))

    def get_queryset(self):
        return Event.objects.past(as_of=timezone.now())


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
