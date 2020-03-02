from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now
from django.views import View
from django.views.generic import DetailView, UpdateView, RedirectView
from django.views.generic.detail import BaseDetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from rest_framework.generics import ListAPIView

from agir.authentication.view_mixins import (
    SoftLoginRequiredMixin,
    PermissionsRequiredMixin,
)
from agir.events.models import Event
from agir.lib.token_bucket import TokenBucket
from agir.lib.views import IframableMixin
from agir.loans.views import (
    BaseLoanAskAmountView,
    BaseLoanPersonalInformationView,
    BaseLoanAcceptContractView,
)
from agir.municipales.actions import generate_cost_certificate
from agir.municipales.forms import (
    CommunePageForm,
    MunicipalesLenderForm,
    MunicipalesAskAmountForm,
    ProcurationForm,
    CostCertificateForm,
)
from agir.municipales.models import CommunePage
from agir.municipales.serializers import CommunePageSerializer
from agir.payments.payment_modes import PAYMENT_MODES

send_procurations_bucket_by_ip = TokenBucket("send_procurations_by_ip", 1, 60)
send_procurations_bucket_by_commune = TokenBucket(
    "send_procurations_by_commune", 10, 30
)


def certificate_path(commune):
    return f"communes/certificates/{commune.code_departement}-{commune.slug}.pdf"


class CommunePageMixin(View):
    context_object_name = "commune"

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.get_queryset(),
            code_departement=self.kwargs["code_departement"],
            slug=self.kwargs["slug"],
        )


class CommuneView(CommunePageMixin, IframableMixin, DetailView):
    queryset = CommunePage.objects.filter(published=True)

    def get_template_names(self):
        if self.request.GET.get("iframe"):
            return ["municipales/commune_details_iframe.html"]
        return ["municipales/commune_details.html"]

    def get_context_data(self, **kwargs):
        events = (
            Event.objects.upcoming()
            .filter(coordinates__intersects=self.object.coordinates)
            .order_by("start_time")
        )
        paginator = Paginator(events, 5)
        kwargs["events"] = paginator.get_page(self.request.GET.get("events_page"))
        kwargs["change_commune"] = self.request.user.has_perm(
            "municipales.change_communepage", self.object
        )

        return super().get_context_data(**kwargs)


class SearchView(ListAPIView):
    serializer_class = CommunePageSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q")

        if not q:
            return CommunePage.objects.none()

        return CommunePage.objects.filter(published=True).search(q)


class CommuneChangeView(
    CommunePageMixin, SoftLoginRequiredMixin, PermissionsRequiredMixin, UpdateView
):
    queryset = CommunePage.objects.filter(published=True)
    form_class = CommunePageForm
    template_name = "municipales/commune_change.html"
    permissions_required = ("municipales.change_communepage",)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["person"] = self.request.user.person
        return kwargs


class CommuneProcurationView(CommunePageMixin, UpdateView):
    queryset = CommunePage.objects.filter(published=True)
    form_class = ProcurationForm
    template_name = "municipales/procuration.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs["person"] = self.request.user.person
        else:
            kwargs["person"] = None
        return kwargs

    def form_valid(self, form):
        if send_procurations_bucket_by_ip.has_tokens(
            self.request.META["REMOTE_ADDR"]
        ) and send_procurations_bucket_by_commune.has_tokens(self.object.id):
            return super().form_valid(form)
        else:
            form.add_error(
                None,
                "Vous venez déjà de faire parvenir votre procurations. Patientez une minute si ce n'est pas le cas.",
            )

            return super().form_invalid(form)

    def get_success_url(self):
        return reverse("view_commune", kwargs=self.kwargs)


class CommuneCostCertificateFormView(CommunePageMixin, SingleObjectMixin, FormView):
    queryset = CommunePage.objects.filter(published=True)
    template_name = "municipales/cost_certificate_form.html"
    permissions_required = ("municipales.change_communepage",)
    form_class = CostCertificateForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "municipales_certificate_download",
            kwargs={
                "code_departement": self.object.code_departement,
                "slug": self.object.slug,
            },
        )

    def form_valid(self, form):
        part = form.cleaned_data["nombre"] / 200000
        generate_cost_certificate(
            {
                "date": now(),
                "pourcentage": "{:.2%}".format(part),
                "montant": int(207097 * part),
                "nom_ville": self.object.name,
                **form.cleaned_data,
            },
            default_storage.path(certificate_path(self.object)),
        )
        return super().form_valid(form)


class CommuneCostCertificateDownloadView(CommunePageMixin, BaseDetailView):
    queryset = CommunePage.objects.filter(published=True)
    permissions_required = ("municipales.change_communepage",)

    def render_to_response(self, context):
        path = certificate_path(context["object"])
        if default_storage.exists(path):
            return FileResponse(default_storage.open(path, "rb"))
        else:
            return redirect(
                "municipales_certificate_form",
                code_departement=self.object.code_departement,
                slug=self.object.slug,
            )


# noinspection PyUnresolvedReferences
class CampagneMixin:
    def dispatch(self, *args, **kwargs):
        self.campagne = self.get_campagne()
        self.commune = self.campagne["commune"]
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["campagne"] = self.campagne
        return kwargs

    def get_campagne(self):
        from agir.municipales.campagnes import get_campagne

        campagne = get_campagne(self.kwargs["code_departement"], self.kwargs["slug"])

        if campagne is None:
            raise Http404("Cette page n'existe pas.")
        return {
            **campagne,
            "commune": CommunePage.objects.get(
                code_departement=campagne["code_departement"], slug=campagne["slug"]
            ),
        }

    def get_meta_title(self):
        return f"Je prête à {self.campagne['nom_liste']}"

    def get_meta_description(self):
        return self.campagne["description"]

    def get_payment_modes(self):
        return [self.campagne["payment_mode"]]

    def get_success_url(self):
        return reverse(
            self.success_view_name,
            kwargs={
                "code_departement": self.commune.code_departement,
                "slug": self.commune.slug,
            },
        )

    def redirect_to_first_step(self):
        if "first_step_url" in self.campagne:
            return redirect(self.campagne["url_montant"])
        return redirect(
            "municipales_loans_ask_amount",
            code_departement=self.commune.code_departement,
            slug=self.commune.slug,
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, campagne=self.campagne)


class CommuneLoanView(CampagneMixin, BaseLoanAskAmountView):
    template_name = "municipales/loans/ask_amount.html"
    success_view_name = "municipales_loans_personal_information"
    form_class = MunicipalesAskAmountForm

    def get(self, request, *args, **kwargs):
        if "url_montant" in self.campagne:
            return redirect(self.campagne["url_montant"])

        return super().get(request, *args, **kwargs)


class CommuneLoanPersonalInformationView(
    CampagneMixin, BaseLoanPersonalInformationView
):
    template_name = "municipales/loans/personal_information.html"
    success_view_name = "municipales_loans_contract"
    base_redirect_view = "municipales_loans_ask_amount"
    payment_type = "pret_municipales"
    form_class = MunicipalesLenderForm

    def prepare_data_for_serialization(self, data):
        # pour s'assurer que la personne créée est forcément en mode non insoumis
        data = super().prepare_data_for_serialization(data)
        data["subscribed"] = False
        return data


class CommuneLoanAcceptContractView(CampagneMixin, BaseLoanAcceptContractView):
    template_name = "municipales/loans/validate_contract.html"
    payment_type = "pret_municipales"

    def get_form_kwargs(self):
        # ne pas inclure campagne pour ce formulaire
        return BaseLoanAcceptContractView.get_form_kwargs(self)


class CommuneLoanReturnView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        mode = PAYMENT_MODES[self.kwargs["payment"].mode]
        return mode.campagne["url_retour"]
