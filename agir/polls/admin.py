import pandas as pd
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from agir.lib.admin.form_fields import AdminJsonWidget
from agir.lib.utils import front_url
from .models import Poll, PollOption


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1
    ordering = ("option_group_id", "created")


class PollAdminForm(forms.ModelForm):
    class Meta:
        widgets = {"rules": AdminJsonWidget()}


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    form = PollAdminForm
    inlines = [PollOptionInline]
    list_display = ("title", "start", "end")
    search_fields = ("title",)
    fields = [
        "title",
        "link",
        "description",
        "confirmation_note",
        "unauthorized_message",
        "start",
        "end",
        "rules",
        "rules_help",
        "options_group_help",
        "tags",
        "authorized_segment",
    ]
    readonly_fields = ["link", "rules_help", "options_group_help"]
    autocomplete_fields = ("authorized_segment",)
    save_as = True

    def link(self, obj):
        if obj.pk:
            return format_html(
                '<a href="{url}">{text}</a>',
                url=front_url("participate_poll", args=[obj.pk]),
                text=_("Voir la consultation"),
            )

    @admin.display(description="Règles disponibles")
    def rules_help(self, _obj):
        doc = pd.DataFrame(
            (
                (
                    "success_url",
                    "string",
                    "L'URL d'une page vers laquelle rédiriger la personne une fois son vote validé",
                ),
                (
                    "verified_user",
                    "boolean=false",
                    "Permet de limiter ou pas le vote aux personnes qui ont un numéro de téléphone validé",
                ),
                (
                    "confirmation_email",
                    "boolean=true",
                    "Permet d'activer ou désactiver l'envoi d'un email de confirmation après validation du vote",
                ),
                (
                    "options",
                    "number",
                    "Permet de spécifier le nombre exacte d'options (par groupe) qu'une personne doit sélectionner "
                    "pour valider son vote",
                ),
                (
                    "min_options",
                    "number",
                    "Permet de spécifier le nombre minimum d'options (par groupe) qu'une personne doit sélectionner "
                    "pour valider son vote (uniquement si aucune valeur n'est définie pour `options`)",
                ),
                (
                    "max_options",
                    "number",
                    "Permet de spécifier le nombre maximum d'options (par groupe) qu'une personne peut sélectionner "
                    "pour valider son vote (uniquement si aucune valeur n'est définie pour `options`)",
                ),
                (
                    "shuffle",
                    "boolean=true",
                    "Permet de définir si les options sont présentées dans un ordre aléatoire (true) ou dans l'ordre "
                    "de création (false)",
                ),
                (
                    "option_groups",
                    "object",
                    "Permet de définir certaines règles spécifiquement pour certains groupes d'options : les clés des "
                    "propriété de l'objet seront les identifiants du groupe d'option, et leur valeur un objet de "
                    "configuration (cf. Règles des groupes d'options)",
                ),
            )
        )
        doc.columns = ["Propriété", "Type", "Description"]
        return mark_safe(doc.to_html(index=False))

    @admin.display(description="Règles des groupes d'options")
    def options_group_help(self, _obj):
        doc = pd.DataFrame(
            (
                (
                    "label",
                    "string='Choix'",
                    "Le libellé du champ affiché pour le groupe d'options",
                ),
                (
                    "help_text",
                    "string",
                    "Un texte d'aide affiché sous le groupe d'option. Si non défini et si des contraintes de nombre "
                    "d'options existent, le texte sera automatiquement défini selon ces contraintes",
                ),
                (
                    "options",
                    "number",
                    "Permet de spécifier le nombre exacte d'options (par groupe) qu'une personne doit sélectionner "
                    "pour valider son vote",
                ),
                (
                    "min_options",
                    "number",
                    "Permet de spécifier le nombre minimum d'options (par groupe) qu'une personne doit sélectionner "
                    "pour valider son vote (uniquement si aucune valeur n'est définie pour `options`)",
                ),
                (
                    "max_options",
                    "number",
                    "Permet de spécifier le nombre maximum d'options (par groupe) qu'une personne peut sélectionner "
                    "pour valider son vote (uniquement si aucune valeur n'est définie pour `options`)",
                ),
                (
                    "shuffle",
                    "boolean",
                    "Permet de définir si les options sont présentées dans un ordre aléatoire (true) ou dans l'ordre "
                    "de création (false)",
                ),
            )
        )
        doc.columns = ["Propriété", "Type", "Description"]
        return mark_safe(doc.to_html(index=False))
