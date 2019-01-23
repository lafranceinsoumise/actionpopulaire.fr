import reversion
from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from functools import partial

from agir.api.admin import admin_site
from agir.donations.actions import history
from agir.lib.admin import AdminViewMixin
from .models import SpendingRequest, Document, Spending


class HandleRequestForm(forms.Form):
    comment = forms.CharField(label="Commentaire", widget=forms.Textarea, required=True)
    status = forms.ChoiceField(
        label="Décision",
        widget=forms.RadioSelect,
        required=True,
        choices=(
            (SpendingRequest.STATUS_VALIDATED, "J'approuve la demande"),
            (
                SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
                "Des informations supplémentaires sont nécessaires",
            ),
            (SpendingRequest.STATUS_REFUSED, "La demande n'est pas admissible"),
        ),
    )


class HandleRequestView(AdminViewMixin, DetailView):
    model = SpendingRequest
    template_name = "admin/donations/handle_request.html"
    form_class = HandleRequestForm
    shown_fields = [
        "id",
        "title",
        "status",
        "group",
        "event",
        "category",
        "category_precisions",
        "explanation",
        "amount",
        "spending_date",
        "provider",
        "iban",
    ]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm("donations.review_spendingrequest"):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        kwargs = {}
        if self.request.method in ["POST", "PUT"]:
            kwargs.update({"data": self.request.POST})

        return self.form_class(**kwargs)

    def get_context_data(self, **kwargs):
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()

        fields = [
            {
                "label": SpendingRequest._meta.get_field(f).verbose_name,
                "value": getattr(self.object, f),
            }
            for f in self.shown_fields
        ]

        return super().get_context_data(
            title="Résumé des événements",
            spending_request=self.object,
            documents=self.object.documents.all(),
            fields=fields,
            history=history(self.object, True),
            **self.get_admin_helpers(kwargs["form"], kwargs["form"].fields),
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            with reversion.create_revision():
                reversion.set_comment(form.cleaned_data["comment"])
                self.object.status = form.cleaned_data["status"]

                if self.object.status == SpendingRequest.STATUS_VALIDATED:
                    try:
                        with transaction.atomic():
                            self.object.operation = Spending.objects.create(
                                group=self.object.group, amount=-self.object.amount
                            )

                    except IntegrityError as e:
                        pass
                    else:
                        self.object.status = SpendingRequest.STATUS_TO_PAY

                self.object.save()

            return HttpResponseRedirect(
                reverse("admin:donations_spendingrequest_changelist")
            )

        return TemplateResponse(
            request, self.template_name, context=self.get_context_data(form=form)
        )


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    can_delete = False


class RequestStatusFilter(admin.SimpleListFilter):
    title = _("Statut")

    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("group", _("En attente du groupe")),
            ("review", _("À revoir")),
            ("to_pay", _("À payer")),
            ("finished", _("Terminées")),
        )

    def queryset(self, request, queryset):
        if self.value() == "group":
            return queryset.filter(status__in=SpendingRequest.STATUS_NEED_ACTION)
        elif self.value() == "review":
            return queryset.filter(status=SpendingRequest.STATUS_AWAITING_REVIEW)
        elif self.value() == "to_pay":
            return queryset.filter(status=SpendingRequest.STATUS_TO_PAY)
        elif self.value() == "finished":
            return queryset.filter(
                status__in=[SpendingRequest.STATUS_PAID, SpendingRequest.STATUS_REFUSED]
            )
        else:
            return queryset.filter()


@admin.register(SpendingRequest, site=admin_site)
class SpendingRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "status",
        "spending_date",
        "group",
        "amount",
        "category",
        "spending_request_actions",
    ]
    sortable_by = ("id", "title", "spending_date", "amount")
    search_fields = ("id", "title", "supportgroup__name")
    list_filter = (RequestStatusFilter,)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "title",
                    "status",
                    "spending_date",
                    "amount",
                    "created",
                    "modified",
                )
            },
        ),
        (_("Groupe et événement"), {"fields": ("group", "event")}),
        (
            _("Détails de la demande"),
            {
                "fields": (
                    "category",
                    "category_precisions",
                    "explanation",
                    "provider",
                    "iban",
                )
            },
        ),
    )

    readonly_fields = ("created", "modified")
    autocomplete_fields = ("group", "event")
    inlines = (DocumentInline,)

    def spending_request_actions(self, obj):
        return format_html(
            '<a href="{url}">{text}</a>',
            url=reverse("admin:donations_spendingrequest_review", args=[obj.pk]),
            text="Traiter",
        )

    spending_request_actions.short_description = "Actions"

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/review/",
                admin_site.admin_view(
                    partial(HandleRequestView.as_view(), model_admin=self)
                ),
                name="donations_spendingrequest_review",
            )
        ] + super().get_urls()
