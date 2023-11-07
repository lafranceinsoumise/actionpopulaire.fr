import os
import re
import textwrap

import ics
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import (
    HttpResponseGone,
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponse,
    Http404,
)
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, DeleteView

from agir.authentication.view_mixins import (
    GlobalOrObjectPermissionRequiredMixin,
    HardLoginRequiredMixin,
)
from agir.carte.models import StaticMapImage
from agir.front.view_mixins import FilterView
from agir.groups.actions.notifications import someone_joined_notification
from agir.groups.filters import GroupFilterSet
from agir.groups.models import SupportGroup, Membership
from agir.lib.geo import get_commune
from agir.lib.tasks import create_static_map_image_from_coordinates
from agir.lib.utils import front_url

__all__ = [
    "SupportGroupListView",
    "SupportGroupIcsView",
    "QuitSupportGroupView",
    "SupportGroupDetailMixin",
    "SuppportGroupOGImageView",
]


class SupportGroupListView(FilterView):
    """List of groups, filter by zipcode"""

    min_items = 20
    template_name = "groups/group_list.html"
    context_object_name = "groups"
    paginate_by = 20
    queryset = SupportGroup.objects.filter(published=True)
    filter_class = GroupFilterSet


class SupportGroupIcsView(DetailView):
    queryset = SupportGroup.objects.active().all()

    def render_to_response(self, context, **response_kwargs):
        calendar = ics.Calendar(
            events=[
                ics.event.Event(
                    name=event.name,
                    begin=event.start_time,
                    end=event.end_time,
                    uid=str(event.pk),
                    description=event.description,
                    location=event.short_address,
                    url=front_url("view_event", args=[event.pk], auto_login=False),
                )
                for event in context["supportgroup"].organized_events.all()
            ]
        )

        return HttpResponse(calendar, content_type="text/calendar")


@method_decorator(never_cache, name="get")
class QuitSupportGroupView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, DeleteView
):
    template_name = "groups/quit.html"
    success_url = reverse_lazy("dashboard")
    queryset = Membership.objects.active().all()
    permission_required = ("groups.delete_membership",)
    context_object_name = "membership"

    def get_object(self, queryset=None):
        try:
            return (
                self.get_queryset()
                .select_related("supportgroup")
                .get(
                    supportgroup__pk=self.kwargs["pk"], person=self.request.user.person
                )
            )
        except Membership.DoesNotExist:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.object.supportgroup
        context["success_url"] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.delete()

        messages.add_message(
            request,
            messages.SUCCESS,
            format_html(
                _("Vous avez bien quitté le groupe <em>{}</em>"),
                self.object.supportgroup.name,
            ),
        )

        return HttpResponseRedirect(success_url)


class SupportGroupDetailMixin(GlobalOrObjectPermissionRequiredMixin):
    permission_required = ("groups.view_supportgroup",)
    queryset = SupportGroup.objects.all()

    def handle_no_permission(self):
        return HttpResponseGone()

    def can_join(self):
        return True

    @method_decorator(login_required(login_url=reverse_lazy("short_code_login")))
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.can_join():
            return HttpResponseRedirect(f'{reverse("join")}')

        if request.POST["action"] == "join":
            if not self.object.open or self.object.is_full:
                return HttpResponseRedirect(
                    reverse("full_group", kwargs={"pk": self.object.pk})
                )
            try:
                with transaction.atomic():
                    membership = Membership.objects.create(
                        supportgroup=self.object,
                        person=request.user.person,
                        membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
                    )
                    someone_joined_notification(
                        membership, membership_count=self.object.active_members_count
                    )
            except IntegrityError:
                pass  # the person is already a member of the group
            return HttpResponseRedirect(
                reverse("view_group", kwargs={"pk": self.object.pk})
            )

        return HttpResponseBadRequest()


class SuppportGroupOGImageView(DetailView):
    model = SupportGroup
    static_root = os.path.join(
        settings.BASE_DIR, "front", "static", "front", "og-image"
    )
    charnieres = {
        "de ": "à ",
        "d'": "à ",
        "du ": "au ",
        "de la ": "à la ",
        "des ": "aux ",
        "de l'": "à l'",
        "de las ": "à las ",
        "de los ": "à los ",
    }

    def get_location_string(self):
        type = self.object.get_type_display()
        city = self.object.location_city
        zip = self.object.location_zip

        if not zip:
            return type

        commune = get_commune(self.object)
        if commune:
            commune = commune.nom_avec_charniere

        if not city and not commune:
            return f"{type} ({zip})"

        if not commune:
            return f"{type} à {city} ({zip})"

        for key, value in self.charnieres.items():
            commune = re.sub("^" + key, value, commune)

        return f"{type} {commune} ({zip})"

    def get_illustration(self):
        if self.object.coordinates is None:
            return self.get_image_from_file("Frame-193.png")

        static_map_image = StaticMapImage.objects.filter(
            center__dwithin=(
                self.object.coordinates,
                StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE,
            ),
        ).first()

        if static_map_image is None:
            create_static_map_image_from_coordinates.delay(
                [self.object.coordinates[0], self.object.coordinates[1]]
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
            filename,
            size=size,
            encoding="utf-8",
            layout_engine=ImageFont.LAYOUT_BASIC,
        )

    def get_image_from_file(self, filename):
        return Image.open(os.path.join(self.static_root, filename))

    def generate_thumbnail(self):
        image = Image.new("RGB", (1200, 630), "#FFFFFF")
        draw = ImageDraw.Draw(image)

        # Draw illustration image
        illustration = self.get_illustration()
        image.paste(illustration, (0, 0), illustration)

        # Draw object subtype and location
        # ex: Groupe local à Paris (75010)
        draw.text(
            (108, 315),
            self.get_location_string(),
            fill=(63, 38, 130, 0),
            align="left",
            font=self.get_font(32, bold=True),
        )

        # Draw object name
        lines = textwrap.wrap(
            self.object.name.capitalize(), width=36, max_lines=2, placeholder="…"
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
        self.object = self.get_object()
        image = self.generate_thumbnail()
        response = HttpResponse(content_type="image/png")
        image.save(response, "PNG")
        return response
