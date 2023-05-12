import json

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ngettext

from agir.activity.models import Activity, Announcement, PushAnnouncement
from agir.lib.search import PrefixSearchQuery


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("timestamp", "type", "recipient", "status", "push_status")}),
        (
            "Éléments liés",
            {"fields": ("event", "supportgroup", "individual", "announcement", "meta")},
        ),
        ("Création et modification", {"fields": ("created", "modified")}),
    )
    list_display = ("type", "timestamp", "recipient", "status", "push_status")
    list_filter = ("type", "status", "push_status")

    readonly_fields = ("created", "modified", "push_status")
    autocomplete_fields = (
        "recipient",
        "event",
        "supportgroup",
        "individual",
    )

    search_fields = ("recipient_search",)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                recipient__search=PrefixSearchQuery(
                    search_term, config="simple_unaccented"
                )
            )

        use_distinct = False

        return queryset, use_distinct


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    MINIATURE_BOX = '<div style="margin: 0 10px;"><h4 style="margin:0;padding:0;">{type}</h4><img src="{link}"></div>'

    fieldsets = (
        (
            "Contenu",
            {
                "fields": (
                    "title",
                    "link",
                    "link_label",
                    "content",
                    "image",
                    "miniatures",
                )
            },
        ),
        (
            "Conditions d'affichage",
            {
                "fields": (
                    "segment",
                    "start_date",
                    "end_date",
                    "priority",
                    "custom_display",
                )
            },
        ),
        ("Statistiques", {"fields": ("affichages", "clics")}),
    )

    readonly_fields = ["miniatures", "affichages", "clics"]
    list_display = ("__str__", "start_date", "end_date")
    autocomplete_fields = ("segment",)

    def miniatures(self, obj):
        if obj is None:
            return "-"

        mobile = format_html(
            self.MINIATURE_BOX, type="mobile", link=obj.image.mobile.url
        )
        desktop = format_html(
            self.MINIATURE_BOX, type="desktop", link=obj.image.desktop.url
        )
        activity = format_html(
            self.MINIATURE_BOX, type="activité", link=obj.image.activity.url
        )

        return format_html(
            '<div style="display:flex;">{mobile}{desktop}{activity}</div>',
            mobile=mobile,
            desktop=desktop,
            activity=activity,
        )

    miniatures.short_description = "Affichage de l'image selon l'environnement"

    def affichages(self, obj):
        if obj.pk:
            return obj.activities.filter(
                status__in=(Activity.STATUS_DISPLAYED, Activity.STATUS_INTERACTED)
            ).count()
        return "-"

    affichages.short_description = "Nombre d'affichages uniques"

    def clics(self, obj):
        if obj.pk:
            return obj.activities.filter(status=Activity.STATUS_INTERACTED).count()

    clics.short_description = "Nombre de clics uniques"


@admin.register(PushAnnouncement)
class PushAnnouncementAdmin(admin.ModelAdmin):
    save_as = True
    save_as_continue = True
    save_on_top = True
    fieldsets = (
        (
            "Paramètres du message",
            {
                "fields": (
                    "title",
                    "subtitle",
                    "message",
                    "link",
                    "image",
                    "thread_id",
                    "ttl",
                    "has_ios",
                    "has_android",
                    "notification_data",
                )
            },
        ),
        (
            "Paramètres de test",
            {
                "fields": (
                    "test_segment",
                    "test_recipient_count",
                    "test_action_buttons",
                )
            },
        ),
        (
            "Paramètres d'envoi",
            {
                "fields": (
                    "segment",
                    "action_buttons",
                )
            },
        ),
        (
            "Statistiques d'envoi",
            {
                "fields": (
                    "sending_date",
                    "recipient_count",
                    "clicked_count",
                    "sending_data",
                )
            },
        ),
    )

    readonly_fields = [
        "notification_data",
        "test_recipient_count",
        "sending_date",
        "sending_data",
        "recipient_count",
        "clicked_count",
        "test_action_buttons",
        "action_buttons",
    ]
    autocomplete_fields = ("segment", "test_segment")

    @admin.display(description="Données")
    def notification_data(self, obj):
        if obj._state.adding:
            return "-"

        android, ios = obj.get_notification_kwargs()
        return format_html(
            "<details>"
            "<summary style='cursor:pointer;'>Données de notification</summary>"
            "<pre>{}</pre>"
            "</details>",
            mark_safe(json.dumps({"android": android, "ios": ios}, indent=2)),
        )

    @admin.display(description="Nombre de destinataires de test")
    def test_recipient_count(self, obj):
        if obj._state.adding or not obj.test_segment:
            return "-"

        return obj.test_recipient_count()

    @admin.display(description="Nombre de destinataires")
    def recipient_count(self, obj):
        if obj._state.adding:
            return "-"

        if obj.can_send():
            return obj.recipient_count()

        return obj.displayed_count()

    @admin.display(description="Nombre de clics")
    def clicked_count(self, obj):
        if obj._state.adding:
            return "-"

        return obj.clicked_count()

    @admin.display(description="Données")
    def sending_data(self, obj):
        if obj._state.adding or not obj.sending_meta:
            return "-"

        return format_html(
            "<details>"
            "<summary style='cursor:pointer;'>Données de l'envoi</summary>"
            "<pre>{}</pre>"
            "</details>",
            mark_safe(json.dumps(obj.sending_meta, indent=2)),
        )

    @admin.display(description="Actions")
    def test_action_buttons(self, obj):
        if obj._state.adding or not obj.test_segment:
            return "-"

        return format_html(
            "<input type='submit' "
            "name='_test' "
            "style='border-radius:8px;background:#f4ed0f;color:#000a2c;font-weight:bold;' "
            "value='📲&ensp;{}' />",
            "ENVOYER AU SEGMENT DE TEST",
        ) + format_html(
            "<div class='help' style='margin: 4px 0 0; padding: 0;'>"
            "Attention : cliquer sur ce bouton recharge la page sans sauvegarder vos modifications courantes."
            "<br />"
            "Les notifications seront envoyées aux appareils des personnes du segment de test spécifié. Aucune notice "
            "d'activité sera créée.<br />Vous pouvez envoyer des notifications de test autant de fois que vous voulez."
            "</div>"
        )

    @admin.display(description="Actions")
    def action_buttons(self, obj):
        if obj._state.adding or not obj.can_send():
            return "-"

        return format_html(
            "<input type='submit' "
            "name='_send' "
            "style='border-radius:8px;background:#571aff;font-weight:bold;' "
            "value='🚀&ensp;{}' />",
            "ENVOYER L'ANNONCE",
        ) + format_html(
            "<div class='help' style='margin: 4px 0 0; padding: 0;'>"
            "Attention : cliquer sur ce bouton recharge la page sans sauvegarder vos modifications courantes."
            "<br />"
            "Les notifications seront envoyées aux appareils des personnes du segment spécifié et des notices "
            "d'activité seront créés pour pouvoir compter le nombre de clics.<br />Une fois l'annonce envoyée il ne sera "
            "plus possible de la renvoyer."
            "</div>"
        )

    def response_change(self, request, obj):
        if "_send" in request.POST:
            try:
                obj.send()
                recipient_count = obj.sending_meta.get("recipients")
                self.message_user(
                    request,
                    ngettext(
                        "L'annonce push a été envoyée à une personne !",
                        f"L'annonce push a été envoyée à {recipient_count} personnes !",
                        recipient_count,
                    ),
                )
            except Exception as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.WARNING,
                )
            return HttpResponseRedirect(".")

        if "_test" in request.POST:
            try:
                result = obj.test()
                result = json.dumps(result, sort_keys=True, indent=2)
                self.message_user(
                    request,
                    mark_safe(f"Résultat de l'envoi de test :<pre>{result}</pre>"),
                )
            except Exception as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.WARNING,
                )
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    class Media:
        pass
