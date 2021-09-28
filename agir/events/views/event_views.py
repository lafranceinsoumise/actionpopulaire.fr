from agir.groups.models import SupportGroup
from agir.activity.models import Activity
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
    UpdateView,
    DeleteView,
    DetailView,
    RedirectView,
    CreateView,
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
from ..filters import EventFilter
from ..forms import (
    EventGeocodingForm,
    EventLegalForm,
    UploadEventImageForm,
    AuthorForm,
)
from ..models import Event, RSVP, OrganizerConfig

from ..tasks import (
    send_event_report,
    send_secretariat_notification,
    send_group_invitation_validated_notification,
)
from ...api import settings
from ...carte.models import StaticMapImage
from django.utils.http import urlencode


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
    "EventThumbnailView",
    "ConfirmEventGroupCoorganization",
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

    def clean_location(self):
        event_details = ""
        location_city = ""
        location_zip = ""

        if self.event.location_city and self.event.location_city != "":
            location_city = self.event.location_city.upper()

        if self.event.location_zip and self.event.location_zip != "":
            location_zip = self.event.location_zip

        if len(location_city) > 0:
            event_details = location_city

        if len(location_zip) > 0:
            if len(location_city) > 0:
                event_details += " (" + location_zip + ") - "
            else:
                event_details = location_zip
        return event_details

    def get_image_font(self, size):
        return ImageFont.truetype(
            os.path.join(self.static_root, "Poppins-Medium.ttf"),
            size=size,
            encoding="utf-8",
            layout_engine=ImageFont.LAYOUT_BASIC,
        )

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

        # Get details of events like "Ville (75000) - Date"
        event_details = self.clean_location()
        event_details += date.upper()

        # For a long event name : display it on 2 lines. Split on the space index to avoid cutting words
        if len(self.event.name) >= 36:
            event_name1 = self.event.name[0:36]
            event_name2 = self.event.name[36:73]
            end = event_name1.rfind(" ")
            if end:
                event_name1 = self.event.name[0:end]
                event_name2 = self.event.name[end + 1 : 73]

        if len(self.event.name) < 30:
            draw.text(
                (108, 350),
                event_details,
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
                event_details,
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
                event_details,
                fill=(87, 26, 255, 0),
                align="left",
                font=font_bold,
            )

            draw.text(
                (108, 369),
                event_name1.capitalize(),
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )
            draw.text(
                (108, 430),
                event_name2,
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )
        else:
            draw.text(
                (108, 319),
                event_details,
                fill=(87, 26, 255, 0),
                align="left",
                font=font_bold,
            )

            draw.text(
                (108, 369),
                event_name1.capitalize(),
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )
            draw.text(
                (108, 430),
                event_name2 + "...",
                fill=(0, 0, 0, 0),
                align="left",
                font=self.get_image_font(45),
            )

        logo_ap = Image.open(os.path.join(self.static_root, "bande-ap.png"))
        logo_ap = logo_ap.resize((1200, 95), Image.ANTIALIAS)
        image.paste(logo_ap, (0, 535), logo_ap)

        return image


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
class ConfirmEventGroupCoorganization(View):
    def get(self, request, pk, *args, **kwargs):

        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("dashboard"))

        event = Event.objects.get(pk=pk)
        group_id = request.GET.get("group")
        group = SupportGroup.objects.get(pk=group_id)
        person = self.request.user.person

        if not event or not group or not person:
            return HttpResponseRedirect(reverse("dashboard"))

        # Check person is organizer of group
        if not person in group.referents:
            return HttpResponseRedirect(reverse("dashboard"))

        # organizers_groups = event.organizers_groups.values_list() # dont work
        organizers_groups = OrganizerConfig.objects.filter(event=event, as_group=group)

        # Check group already coorganizer
        if len(organizers_groups) > 0:
            params = {
                "toast": True,
                "type": "INFO",
                "text": "Votre groupe est déjà coorganisateur",
            }
            return HttpResponseRedirect(
                reverse("view_event", kwargs={"pk": pk}) + "?" + urlencode(params)
            )

        activity_groups_invited = Activity.objects.filter(
            event=event, type=Activity.TYPE_GROUP_COORGANIZATION_INVITE,
        )
        # .distinct("supportgroup") # dont work
        groups_invited = SupportGroup.objects.filter(
            pk__in=activity_groups_invited.values_list("supportgroup")
        )

        # Check group have been invited to event
        if not group in groups_invited:
            params = {
                "toast": True,
                "type": "ERROR",
                "text": "Une erreure est apparue",
            }
            return HttpResponseRedirect(
                reverse("view_event", kwargs={"pk": pk}) + "?" + urlencode(params)
            )

        # Get current organizers of event to send them notification
        event_organizers_id = list(event.organizers.all().values_list("id"))

        # Add group with validating referent as organizer of the event
        organizer_config = OrganizerConfig.objects.create(
            event=event, as_group=group, person=person
        )
        organizer_config.save()

        # Delete activities TYPE_GROUP_COORGANIZATION_INVITE, replaced by ACCEPTED ones in task
        activity_groups_invited.filter(supportgroup=group).delete()

        send_group_invitation_validated_notification.delay(pk, group_id)
        # send_group_invitation_validated_notification.delay(pk, group_id, event_organizers_id)
        return HttpResponseRedirect(reverse("view_event", kwargs={"pk": pk}) + "?toast")


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
