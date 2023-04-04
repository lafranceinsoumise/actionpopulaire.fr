from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agir.donations.models import Operation, SpendingRequest, Document
from agir.groups.models import SupportGroup, Membership
from agir.payments.models import Payment
from agir.people.models import Person


def round_date_like_reversion(d):
    return d.replace(microsecond=d.microsecond // 1000 * 1000)


class SpendingRequestTestCase(TestCase):
    def setUp(self):
        self.p1 = Person.objects.create_insoumise("test1@test.com", create_role=True)
        self.p2 = Person.objects.create_insoumise("test2@test.com", create_role=True)
        self.treasurer = Person.objects.create_superperson(
            "treasurer@example.com", "huhuihui"
        )

        self.group1 = SupportGroup.objects.create(
            name="Groupe 1",
            type=SupportGroup.TYPE_LOCAL_GROUP,
            certification_date=timezone.now(),
        )

        self.membership1 = Membership.objects.create(
            person=self.p1,
            supportgroup=self.group1,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.membership2 = Membership.objects.create(
            person=self.p2,
            supportgroup=self.group1,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.payment = Payment.objects.create(
            status=Payment.STATUS_COMPLETED, price=1000, type="don", mode="system_pay"
        )

        self.allocation = Operation.objects.create(
            payment=self.payment, amount=1000, group=self.group1
        )

        date = (timezone.now() + timezone.timedelta(days=20)).date()

        self.spending_request_data = {
            "title": "Ma demande de dépense",
            "event": None,
            "category": SpendingRequest.CATEGORY_HARDWARE,
            "category_precisions": "Super truc trop cool",
            "explanation": "On en a VRAIMENT VRAIMENT besoin.",
            "spending_date": date,
            "provider": "Super CLIENT",
            "iban": "FR96 9643 9954 500A 9L6K Z94T W60",
            "amount": 8500,
        }

        file = SimpleUploadedFile(
            "document.odt",
            b"Un faux fichier",
            content_type="application/vnd.oasis.opendocument.text",
        )

        self.form_data = {
            **self.spending_request_data,
            "event": "",
            "amount": "85.00",
            "documents-TOTAL_FORMS": "3",
            "documents-INITIAL_FORMS": "0",
            "documents-MIN_NUM_FORMS": "0",
            "documents-0-title": "Facture",
            "documents-0-type": Document.TYPE_INVOICE,
            "documents-0-file": file,
        }

    def test_can_create_spending_request(self):
        """Peut créer une demande de paiement"""
        self.client.force_login(self.p1.role)

        res = self.client.get(
            reverse("create_spending_request", args=(self.group1.pk,))
        )

        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse("create_spending_request", args=(self.group1.pk,)),
            data=self.form_data,
        )

        spending_request = SpendingRequest.objects.get()

        self.assertRedirects(
            res, reverse("manage_spending_request", args=(spending_request.pk,))
        )

        self.assertEqual(
            spending_request.get_history(),
            [
                {
                    "title": "Création de la demande",
                    "user": self.p1.get_short_name(),
                    "modified": round_date_like_reversion(spending_request.modified),
                    "comment": "Création de la demande",
                    "diff": [],
                }
            ],
        )

    def test_can_manage_spending_request(self):
        """Peut accéder à la page de gestion d'une demande"""
        self.client.force_login(self.p1.role)

        spending_request = SpendingRequest.objects.create(
            group=self.group1, **self.spending_request_data
        )

        res = self.client.get(
            reverse("manage_spending_request", args=(spending_request.pk,))
        )
        self.assertEqual(res.status_code, 200)

    def test_can_edit_spending_request(self):
        """Peut modifier une demande de paiment"""
        self.client.force_login(self.p1.role)
        spending_request = SpendingRequest.objects.create(
            group=self.group1, **self.spending_request_data
        )

        res = self.client.get(
            reverse("edit_spending_request", args=(spending_request.pk,))
        )
        self.assertEqual(res.status_code, 200)

        self.form_data["amount"] = "77"
        self.form_data["comment"] = "Petite modification du montant"
        res = self.client.post(
            reverse("edit_spending_request", args=(spending_request.pk,)),
            data=self.form_data,
        )
        self.assertRedirects(
            res, reverse("manage_spending_request", args=(spending_request.pk,))
        )

        spending_request.refresh_from_db()
        self.assertEqual(spending_request.amount, 7700)

    def test_can_add_document(self):
        """Un gestionnaire du groupe peut ajouter un document justificatif à une demande"""
        self.client.force_login(self.p1.role)
        spending_request = SpendingRequest.objects.create(
            group=self.group1, **self.spending_request_data
        )

        res = self.client.get(reverse("create_document", args=(spending_request.pk,)))
        self.assertEqual(res.status_code, 200)

        file = SimpleUploadedFile(
            "document.odt",
            b"Un faux fichier",
            content_type="application/vnd.oasis.opendocument.text",
        )

        res = self.client.post(
            reverse("create_document", args=(spending_request.pk,)),
            data={
                "title": "Mon super fichier",
                "type": Document.TYPE_INVOICE,
                "file": file,
            },
        )
        self.assertRedirects(
            res, reverse("manage_spending_request", args=(spending_request.pk,))
        )

        self.assertEqual(len(spending_request.documents.all()), 1)
        self.assertEqual(spending_request.documents.first().title, "Mon super fichier")

    def test_can_modify_document(self):
        """Un gestionnaire du groupe peut modifier un des documents justificatifs"""
        self.client.force_login(self.p1.role)
        spending_request = SpendingRequest.objects.create(
            group=self.group1, **self.spending_request_data
        )

        file1 = SimpleUploadedFile(
            "document.odt",
            b"Un faux fichier",
            content_type="application/vnd.oasis.opendocument.text",
        )

        file2 = SimpleUploadedFile(
            "document.odt",
            b"Un autre document",
            content_type="application/vnd.oasis.opendocument.text",
        )

        document = Document.objects.create(
            title="Mon document",
            request=spending_request,
            type=Document.TYPE_INVOICE,
            file=file1,
        )

        res = self.client.get(
            reverse("edit_document", args=(spending_request.pk, document.pk))
        )
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse("edit_document", args=(spending_request.pk, document.pk)),
            data={
                "title": "Mon SUPER document",
                "type": Document.TYPE_OTHER,
                "file": file2,
            },
        )
        self.assertRedirects(
            res, reverse("manage_spending_request", args=(spending_request.pk,))
        )

    def test_admin_can_validate_without_funds(self):
        """Un membre de l'équipe de suivi peut valider une demande même sans fonds"""
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )
        spending_request = SpendingRequest.objects.create(
            group=self.group1,
            **self.spending_request_data,
            status=SpendingRequest.STATUS_AWAITING_REVIEW,
        )

        res = self.client.get(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            )
        )
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            ),
            data={"comment": "C'est bon !", "status": SpendingRequest.STATUS_VALIDATED},
        )
        self.assertRedirects(res, reverse("admin:donations_spendingrequest_changelist"))

        spending_request.refresh_from_db()
        self.assertEqual(spending_request.status, SpendingRequest.STATUS_VALIDATED)

    def test_admin_can_validate_with_funds(self):
        """Un membre de l'équipe de suivi peut valider une demande même sans fonds"""
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )

        # devrait être assez, en comptant celle de 1000 déjà existante
        Operation.objects.create(amount=8000, group=self.group1)

        spending_request = SpendingRequest.objects.create(
            group=self.group1,
            **self.spending_request_data,
            status=SpendingRequest.STATUS_AWAITING_REVIEW,
        )

        res = self.client.get(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            )
        )
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            ),
            data={"comment": "C'est bon !", "status": SpendingRequest.STATUS_VALIDATED},
        )
        self.assertRedirects(res, reverse("admin:donations_spendingrequest_changelist"))

        spending_request.refresh_from_db()
        self.assertEqual(spending_request.status, SpendingRequest.STATUS_TO_PAY)

        operation = spending_request.operation
        self.assertIsNotNone(operation)
        self.assertEqual(operation.group, self.group1)
        self.assertEqual(operation.amount, -8500)

    def test_history_is_correct(self):
        """L'historique d'une demande de dépense est correctement généré"""
        self.maxDiff = None

        self.client.force_login(self.p1.role)

        # création
        self.client.post(
            reverse("create_spending_request", args=(self.group1.pk,)),
            data=self.form_data,
        )

        spending_request = SpendingRequest.objects.get()
        spending_request_id = spending_request.pk

        # modification d'un champ
        self.form_data["explanation"] = "C'est vachement important"
        self.client.post(
            reverse("edit_spending_request", args=(spending_request_id,)),
            data={**self.form_data, "comment": "J'ai renforcé mon explication !"},
        )

        # première validation
        self.client.post(
            reverse("manage_spending_request", args=(spending_request_id,)),
            data={"validate": SpendingRequest.STATUS_DRAFT},
        )

        # seconde validation
        self.client.force_login(self.p2.role)
        self.client.post(
            reverse("manage_spending_request", args=(spending_request_id,)),
            data={"validate": SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION},
        )

        # ajout d'un document oublié ==> retour à l'étape de validation
        file = SimpleUploadedFile(
            "document.odt",
            b"Un faux fichier",
            content_type="application/vnd.oasis.opendocument.text",
        )
        self.client.post(
            reverse("create_document", args=(spending_request_id,)),
            data={
                "title": "Document complémentaire",
                "type": Document.TYPE_OTHER,
                "file": file,
            },
        )

        # renvoi vers l'équipe de suivi
        self.client.post(
            reverse("manage_spending_request", args=(spending_request_id,)),
            data={
                "validate": SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION
            },
        )

        # demande d'informations supplémentaires
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )
        self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request_id,)
            ),
            data={
                "comment": "Le montant ne correspond pas à la facture !",
                "status": SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
            },
        )

        # modification du document
        self.client.force_login(self.p1.role)
        self.form_data["amount"] = 8400
        self.client.post(
            reverse("edit_spending_request", args=(spending_request_id,)),
            data={
                **self.form_data,
                "comment": "J'ai corrigé le montant... j'avais mal lu !",
            },
        )

        # renvoi vers l'équipe de suivi
        self.client.post(
            reverse("manage_spending_request", args=(spending_request_id,)),
            data={
                "validate": SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION
            },
        )

        # acceptation
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )
        self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request_id,)
            ),
            data={
                "comment": "Tout est parfait !",
                "status": SpendingRequest.STATUS_VALIDATED,
            },
        )

        hist = spending_request.get_history()
        for d in hist:
            del d["modified"]

        self.assertEqual(
            hist,
            [
                {
                    "title": "Création de la demande",
                    "user": self.p1.get_short_name(),
                    "comment": "Création de la demande",
                    "diff": [],
                },
                {
                    "title": "Modification de la demande",
                    "user": self.p1.get_short_name(),
                    "comment": "J'ai renforcé mon explication !",
                    "diff": ["Justification de la demande"],
                },
                {
                    "title": "Validé par l'auteur d'origine",
                    "user": self.p1.get_short_name(),
                    "comment": "",
                    "diff": [],
                },
                {
                    "title": "Validé par un⋅e second⋅e animateur⋅rice",
                    "user": self.p2.get_short_name(),
                    "comment": "",
                    "diff": [],
                },
                {
                    "title": "Modification de la demande",
                    "user": self.p2.get_short_name(),
                    "diff": [],
                    "comment": "Ajout d'un document",
                },
                {
                    "title": "Renvoyé pour validation à l'équipe de suivi des questions financières",
                    "user": self.p2.get_short_name(),
                    "comment": "",
                    "diff": [],
                },
                {
                    "title": "Informations supplémentaires requises",
                    "user": "Équipe de suivi",
                    "comment": "Le montant ne correspond pas à la facture !",
                    "diff": [],
                },
                {
                    "comment": "J'ai corrigé le montant... j'avais mal lu !",
                    "diff": ["Montant de la dépense"],
                    "title": "Modification de la demande",
                    "user": self.p1.get_short_name(),
                },
                {
                    "title": "Renvoyé pour validation à l'équipe de suivi des questions financières",
                    "user": self.p1.get_short_name(),
                    "comment": "",
                    "diff": [],
                },
                {
                    "comment": "Tout est parfait !",
                    "diff": [],
                    "title": "Demande validée par l'équipe de suivi des questions financières",
                    "user": "Équipe de suivi",
                },
            ],
        )
