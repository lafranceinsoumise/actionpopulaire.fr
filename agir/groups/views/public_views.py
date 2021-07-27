import os

import ics
from PIL import Image, ImageDraw, ImageFont

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
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, DeleteView, ListView

from agir.api import settings
from agir.authentication.view_mixins import (
    GlobalOrObjectPermissionRequiredMixin,
    HardLoginRequiredMixin,
)
from agir.carte.models import StaticMapImage
from agir.front.view_mixins import FilterView
from agir.groups.actions.notifications import someone_joined_notification
from agir.groups.filters import GroupFilterSet
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.lib.utils import front_url

__all__ = [
    "SupportGroupListView",
    "SupportGroupIcsView",
    "QuitSupportGroupView",
    "ThematicTeamsViews",
    "SupportGroupDetailMixin",
]


class SupportGroupListView(FilterView):
    """List of groups, filter by zipcode
    """

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


class ThematicTeamsViews(ListView):
    template_name = "groups/thematic_teams.html"
    context_object_name = "groups"

    def get_queryset(self):
        subtype = SupportGroupSubtype.objects.get(label="rédaction du livret")
        return SupportGroup.objects.active().filter(subtypes=subtype).order_by("name")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, default_image="front/images/AEC-mini.png"
        )


class SupportGroupDetailMixin(GlobalOrObjectPermissionRequiredMixin):
    permission_required = ("groups.view_supportgroup",)
    meta_description = "Rejoignez les groupes d'action de votre quartier pour la candidature de Jean-Luc Mélenchon pour 2022"
    queryset = SupportGroup.objects.all()
    bundle_name = "front/app"
    data_script_id = "exportedGroup"

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
            if self.object.is_full:
                return HttpResponseRedirect(
                    reverse("full_group", kwargs={"pk": self.object.pk})
                )
            try:
                with transaction.atomic():
                    membership = Membership.objects.create(
                        supportgroup=self.object, person=request.user.person
                    )
                    someone_joined_notification(
                        membership, membership_count=self.object.members_count
                    )
            except IntegrityError:
                pass  # the person is already a member of the group
            return HttpResponseRedirect(
                reverse("view_group", kwargs={"pk": self.object.pk})
            )

        return HttpResponseBadRequest()


class GroupThumbnailView(DetailView):
    model = SupportGroup
    group = None
    static_root = "{}/agir/front/static/front/og-image/".format(os.getcwd())

    def get(self, request, *args, **kwargs):
        self.group = self.get_object()

        image = self.generate_thumbnail()
        response = HttpResponse(content_type="image/png")
        image.save(response, "PNG")
        return response

    def generate_thumbnail(self):
        group_type = self.group.type

        image = Image.new("RGB", (int(1200), int(630)), "#FFFFFF")
        draw = ImageDraw.Draw(image)

        bandeau = Image.open(self.static_root + "bandeau-ap-centre.png")
        bandeau = bandeau.resize((1200, 95), Image.ANTIALIAS)
        image.paste(bandeau, (0, 535), bandeau)

        for type in self.group.TYPE_CHOICES:
            u, v = type
            if u == self.group.type:
                group_type = v

        if self.group.coordinates is None:
            illustration = Image.open(self.static_root + "Frame-193.png")
            image.paste(illustration, (0, 0), illustration)
        else:
            static_map_image = StaticMapImage.objects.filter(
                center__distance_lt=(
                    self.group.coordinates,
                    StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE,
                ),
            ).first()

            illustration = Image.open(static_map_image.image.path)
            illustration = illustration.resize((1200, 225), Image.ANTIALIAS)
            image.paste(illustration, (0, 0), illustration)

            if self.group.image:
                avatar = Image.open(self.group.image.path)
            else:
                avatar = Image.open(self.static_root + "avatar.png")
            avatar = avatar.resize((148, 148), Image.ANTIALIAS)
            image.paste(avatar, (526, 130), avatar)

        if len(self.group.name) < 30:
            if self.group.location_city is not None:
                draw.text(
                    (390, 350),
                    "{} À {} ({})".format(
                        group_type, self.group.location_city, self.group.location_zip
                    ).upper(),
                    fill=(87, 26, 255, 0),
                    align="center",
                    font=self.get_image_font(27),
                )

            draw.text(
                (389, 400),
                self.group.name.capitalize(),
                fill=(0, 0, 0, 0),
                align="center",
                font=self.get_image_font(45),
            )

        elif len(self.group.name) < 36:
            if self.group.location_city is not None:
                draw.text(
                    (390, 350),
                    "{} À {} ({})".format(
                        group_type, self.group.location_city, self.group.location_zip
                    ).upper(),
                    fill=(87, 26, 255, 0),
                    align="center",
                    font=self.get_image_font(27),
                )

            draw.text(
                (389, 350),
                group_type.upper(),
                fill=(87, 26, 255, 0),
                align="center",
                font=self.get_image_font(27),
            )
            draw.text(
                (389, 400),
                self.group.name.capitalize(),
                fill=(0, 0, 0, 0),
                align="center",
                font=self.get_image_font(45),
            )
        elif len(self.group.name) < 40:
            if self.group.location_city is not None:
                draw.text(
                    (390, 350),
                    "{} À {} ({})".format(
                        group_type, self.group.location_city, self.group.location_zip
                    ).upper(),
                    fill=(87, 26, 255, 0),
                    align="center",
                    font=self.get_image_font(27),
                )

            draw.text(
                (330, 370),
                self.group.name[0:26].capitalize(),
                fill=(0, 0, 0, 0),
                align="center",
                font=self.get_image_font(45),
            )
            draw.text(
                (120, 430),
                self.group.name[27:39].capitalize(),
                fill=(0, 0, 0, 0),
                align="center",
                font=self.get_image_font(45),
            )

        else:
            if self.group.location_city is not None:
                draw.text(
                    (390, 320),
                    "{} À {} ({})".format(
                        group_type, self.group.location_city, self.group.location_zip
                    ).upper(),
                    fill=(87, 26, 255, 0),
                    align="center",
                    font=self.get_image_font(27),
                )

            draw.text(
                (330, 370),
                self.group.name[0:26].capitalize(),
                fill=(0, 0, 0, 0),
                align="center",
                font=self.get_image_font(45),
            )
            draw.text(
                (120, 430),
                self.group.name[27:64] + "...",
                fill=(0, 0, 0, 0),
                align="center",
                font=self.get_image_font(45),
            )

        return image

    def get_image_font(self, size):
        return ImageFont.truetype(
            self.static_root + "Poppins-Medium.ttf",
            size=size,
            encoding="utf-8",
            layout_engine=ImageFont.LAYOUT_BASIC,
        )
