from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from reversion.models import Version

from agir.donations.models import SpendingRequest, Document, AccountOperation
from agir.groups.models import SupportGroup, Membership
from agir.lib.tests.test_utils import multipartify
from agir.payments.models import Payment
from agir.people.models import Person


def round_date_like_reversion(d):
    return d.replace(microsecond=d.microsecond // 1000 * 1000)


class SpendingRequestTestCase(APITestCase):
    def setUp(self):
        self.group_finance_admin = Person.objects.create_insoumise(
            "test1@test.com", create_role=True
        )
        self.another_group_finance_admin = Person.objects.create_insoumise(
            "test2@test.com", create_role=True
        )
        self.group_member = Person.objects.create_insoumise(
            "test3@test.com", create_role=True
        )
        self.another_person = Person.objects.create_insoumise(
            "test4@test.com", create_role=True
        )

        self.treasurer = Person.objects.create_superperson(
            "treasurer@example.com", "huhuihui"
        )

        self.group = SupportGroup.objects.create(
            name="Groupe 1",
            type=SupportGroup.TYPE_LOCAL_GROUP,
            certification_date=timezone.now(),
        )

        Membership.objects.create(
            person=self.group_finance_admin,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        Membership.objects.create(
            person=self.another_group_finance_admin,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        Membership.objects.create(
            person=self.group_member,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        date = (timezone.now() + timezone.timedelta(days=20)).date()

        self.valid_data = {
            "title": "Ma demande de dépense",
            "timing": SpendingRequest.Timing.UPCOMING,
            "groupId": str(self.group.pk),
            "eventId": "",
            "category": SpendingRequest.Category.SALLE,
            "explanation": "On en a VRAIMENT VRAIMENT besoin.",
            "spendingDate": date,
            "bankAccount": {
                "name": "Super CLIENT",
                "iban": "FR96 9643 9954 500A 9L6K Z94T W60",
                "bic": "ABNAFRPP",
                "rib": SimpleUploadedFile(
                    "rib.pdf",
                    b"Le Releve d'Identite Bancaire",
                    content_type="application/pdf",
                ),
            },
            "amount": 8500,
            "contact": {
                "name": "Gégène",
                "phone": "+33600000000",
            },
            "shouldValidate": False,
        }

        self.existing_spending_request = SpendingRequest.objects.create(
            title="Existing spending request",
            timing=SpendingRequest.Timing.PAST,
            group_id=str(self.group.pk),
            category=SpendingRequest.Category.SALLE,
            amount=1000,
            spending_date=(timezone.now() - timezone.timedelta(days=20)).date(),
        )

    def get_form_data(self, data=None, with_docs=False):
        form_data = {**self.valid_data}

        if with_docs:
            form_data["attachments"] = [
                {
                    "title": "Facture",
                    "type": Document.Type.INVOICE.value,
                    "file": SimpleUploadedFile(
                        "document.pdf", b"Un document", content_type="application/pdf"
                    ),
                }
            ]

        if data:
            form_data = {**form_data, **data}

        return multipartify(form_data)

    def create_spending_request(
        self, data=None, without_funds=False, return_response=False
    ):
        if data is None:
            data = self.get_form_data(with_docs=True)

        if not without_funds:
            payment = Payment.objects.create(
                status=Payment.STATUS_COMPLETED,
                price=data["amount"][1],
                type="don",
                mode="system_pay",
            )
            AccountOperation.objects.create(
                payment=payment,
                amount=data["amount"][1],
                source="revenu:dons",
                destination=f"actif:groupe:{self.group.id}",
            )

        res = self.client.post(
            reverse("api_spending_request_create"),
            data=data,
            format="multipart",
        )

        if return_response:
            return res

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        spending_request = SpendingRequest.objects.get(id=res.data["id"])

        return spending_request

    def test_anonymous_cannot_create_retrieve_edit_or_delete_a_request(self):
        self.client.logout()
        res = self.create_spending_request(return_response=True)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.get(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            ),
            data=multipartify(
                {
                    "amount": 1000,
                    "comment": "Petite modification du montant",
                }
            ),
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.delete(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_create_retrieve_edit_or_delete_documents(self):
        self.client.logout()
        spending_request_pk = self.existing_spending_request.pk
        document = Document.objects.create(
            title="Doc",
            type=Document.Type.OTHER,
            file=SimpleUploadedFile(
                "document.png",
                b"Un faux fichier",
                content_type="image/png",
            ),
            request_id=spending_request_pk,
        )
        res = self.client.post(
            reverse(
                "api_spending_request_document_create", args=(spending_request_pk,)
            ),
            data={
                "title": "Mon super fichier",
                "type": Document.Type.INVOICE,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.get(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.patch(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            ),
            data={
                "title": "Mon SUPER document",
                "type": Document.Type.OTHER,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.delete(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_group_member_cannot_create_retrieve_edit_or_delete_a_request(self):
        self.client.force_login(self.another_person.role)
        res = self.create_spending_request(return_response=True)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            ),
            data=multipartify(
                {
                    "amount": 1000,
                    "comment": "Petite modification du montant",
                }
            ),
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.delete(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_group_member_cannot_create_retrieve_edit_or_delete_documents(self):
        self.client.force_login(self.another_person.role)
        spending_request_pk = self.existing_spending_request.pk
        document = Document.objects.create(
            title="Doc",
            type=Document.Type.OTHER,
            file=SimpleUploadedFile(
                "document.png",
                b"Un faux fichier",
                content_type="image/png",
            ),
            request_id=spending_request_pk,
        )
        res = self.client.post(
            reverse(
                "api_spending_request_document_create", args=(spending_request_pk,)
            ),
            data={
                "title": "Mon super fichier",
                "type": Document.Type.INVOICE,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.patch(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            ),
            data={
                "title": "Mon SUPER document",
                "type": Document.Type.OTHER,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.delete(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_simple_group_member_cannot_create_retrieve_edit_or_delete_a_request(self):
        self.client.force_login(self.group_member.role)
        res = self.create_spending_request(return_response=True)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            ),
            data=multipartify(
                {"amount": 1000, "comment": "Petite modification du montant"}
            ),
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.delete(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_simple_group_member_cannot_create_retrieve_edit_or_delete_documents(self):
        self.client.force_login(self.group_member.role)
        spending_request_pk = self.existing_spending_request.pk
        document = Document.objects.create(
            title="Doc",
            type=Document.Type.OTHER,
            file=SimpleUploadedFile(
                "document.png",
                b"Un faux fichier",
                content_type="image/png",
            ),
            request_id=spending_request_pk,
        )
        res = self.client.post(
            reverse(
                "api_spending_request_document_create", args=(spending_request_pk,)
            ),
            data={
                "title": "Mon super fichier",
                "type": Document.Type.INVOICE,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.patch(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            ),
            data={
                "title": "Mon SUPER document",
                "type": Document.Type.OTHER,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.delete(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_finance_admin_can_create_retrieve_edit_or_delete_a_request(self):
        self.client.force_login(self.group_finance_admin.role)
        res = self.create_spending_request(return_response=True)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data, res.data)
        spending_request = SpendingRequest.objects.get(pk=res.data["id"])
        res = self.client.get(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request.pk,),
            ),
            data=multipartify(
                {"amount": 1000, "comment": "Petite modification du montant"}
            ),
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.delete(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_group_finance_admin_can_create_retrieve_edit_or_delete_documents(self):
        self.client.force_login(self.group_finance_admin.role)
        spending_request_pk = self.existing_spending_request.pk
        document = Document.objects.create(
            title="Doc",
            type=Document.Type.OTHER,
            file=SimpleUploadedFile(
                "document.png",
                b"Un faux fichier",
                content_type="image/png",
            ),
            request_id=spending_request_pk,
        )
        res = self.client.post(
            reverse(
                "api_spending_request_document_create", args=(spending_request_pk,)
            ),
            data={
                "title": "Mon super fichier",
                "type": Document.Type.INVOICE,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.get(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            ),
            data={
                "title": "Mon SUPER document",
                "type": Document.Type.OTHER,
                "file": SimpleUploadedFile(
                    "document.png",
                    b"Un faux fichier",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.delete(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_create_spending_request(self):
        """Peut créer une demande de paiement"""
        self.client.force_login(self.group_finance_admin.role)

        res = self.client.options(reverse("api_spending_request_create"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        spending_request = self.create_spending_request()
        version = Version.objects.get_for_object(spending_request).first()

        self.assertEqual(
            spending_request.get_history(),
            [
                {
                    "id": version.pk,
                    "title": "Création de la demande",
                    "person": self.group_finance_admin,
                    "modified": round_date_like_reversion(spending_request.modified),
                    "comment": "",
                    "diff": [],
                    "status": SpendingRequest.Status.DRAFT,
                }
            ],
        )

    def test_can_delete_spending_request(self):
        """Peut créer une demande de paiement"""
        self.client.force_login(self.group_finance_admin.role)

        res = self.client.options(reverse("api_spending_request_create"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        spending_request = self.create_spending_request()
        spending_request_pk = spending_request.pk

        res = self.client.delete(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(SpendingRequest.DoesNotExist):
            SpendingRequest.objects.get(pk=spending_request_pk)

    def test_can_retrieve_spending_request_details(self):
        """Peut accéder aux détails d'une demande"""
        self.client.force_login(self.group_finance_admin.role)

        res = self.client.get(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(self.existing_spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            res.data.get("group"),
            {
                "id": str(self.existing_spending_request.group.pk),
                "name": self.existing_spending_request.group.name,
            },
        )

    def test_can_edit_spending_request(self):
        """Peut modifier une demande de paiment"""
        self.client.force_login(self.group_finance_admin.role)

        spending_request = self.create_spending_request()
        new_amount = 7799
        self.assertNotEqual(spending_request.amount, new_amount)
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request.pk,),
            ),
            data=multipartify(
                {
                    "amount": new_amount,
                    "comment": "Petite modification du montant",
                    "bankAccount": {
                        "rib": SimpleUploadedFile(
                            "rib2.pdf",
                            b"Le BON RIB",
                            content_type="application/pdf",
                        ),
                    },
                }
            ),
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertEqual(res.data.get("amount"), new_amount)
        self.assertEqual(len(res.data["history"]), 2)
        spending_request.refresh_from_db()
        self.assertEqual(spending_request.amount, new_amount)

        last_history_item = res.data["history"].pop()
        self.assertEqual(
            last_history_item["comment"],
            "Petite modification du montant",
        )
        self.assertListEqual(
            last_history_item["diff"], ["Montant de la dépense", "RIB"]
        )

    def test_can_add_document(self):
        """Un gestionnaire du groupe peut ajouter un document justificatif à une demande"""
        self.client.force_login(self.group_finance_admin.role)

        spending_request = self.create_spending_request(data=self.get_form_data())
        self.assertEqual(len(spending_request.attachments), 0)

        unsupported_file = SimpleUploadedFile(
            "document.odt",
            b"Un faux fichier",
            content_type="application/vnd.oasis.opendocument.text",
        )

        res = self.client.post(
            reverse(
                "api_spending_request_document_create", args=(spending_request.pk,)
            ),
            data={
                "title": "Mon super fichier",
                "type": Document.Type.INVOICE,
                "file": unsupported_file,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("file", res.data)
        self.assertEqual(spending_request.documents.count(), 0)

        file = SimpleUploadedFile(
            "document.png",
            b"Un faux fichier",
            content_type="image/png",
        )

        res = self.client.post(
            reverse(
                "api_spending_request_document_create", args=(spending_request.pk,)
            ),
            data={
                "title": "Mon super fichier",
                "type": Document.Type.INVOICE,
                "file": file,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(spending_request.documents.count(), 1)
        self.assertEqual(spending_request.documents.first().title, "Mon super fichier")

        res = self.client.get(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["history"]), 2, res.data)
        self.assertEqual(len(res.data["attachments"]), 1)

    def test_can_modify_document(self):
        """Un gestionnaire du groupe peut modifier un des documents justificatifs"""
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request(data=self.get_form_data())
        self.assertEqual(len(spending_request.attachments), 0)

        file1 = SimpleUploadedFile(
            "document.pdf",
            b"Un faux fichier",
            content_type="application/pdf",
        )

        file2 = SimpleUploadedFile(
            "document.pdf",
            b"Un autre document",
            content_type="application/pdf",
        )

        document = Document.objects.create(
            title="Mon document",
            request=spending_request,
            type=Document.Type.INVOICE,
            file=file1,
        )

        res = self.client.get(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], document.title)
        self.assertEqual(res.data["type"], document.type)

        res = self.client.patch(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            ),
            data={
                "title": "Mon SUPER document",
                "type": Document.Type.OTHER,
                "file": file2,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertEqual(res.data["title"], "Mon SUPER document")
        self.assertEqual(res.data["type"], Document.Type.OTHER)
        document.refresh_from_db()
        self.assertEqual(res.data["title"], document.title)
        self.assertEqual(res.data["type"], document.type)

    def test_can_delete_document(self):
        """Un gestionnaire du groupe peut modifier un des documents justificatifs"""
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request(data=self.get_form_data())
        self.assertEqual(len(spending_request.attachments), 0)

        document = Document.objects.create(
            title="Mon document",
            request=spending_request,
            type=Document.Type.INVOICE,
            file=SimpleUploadedFile(
                "document.pdf",
                b"Un faux fichier",
                content_type="application/pdf",
            ),
        )
        self.assertFalse(document.deleted)
        res = self.client.delete(
            reverse(
                "api_spending_request_document_retrieve_update_delete",
                args=(document.pk,),
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        document.refresh_from_db()
        self.assertTrue(document.deleted)
        self.assertNotIn(document, spending_request.attachments)

    def test_can_send_request_to_peer_review_upon_creation(self):
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request(
            data=self.get_form_data(data={"shouldValidate": True}, with_docs=True)
        )
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_PEER_REVIEW
        )

    def test_can_send_request_to_peer_review_upon_edition(self):
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request()
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request.pk,),
            ),
            data={
                "amount": 1000,
                "comment": "Petite modification du montant",
                "shouldValidate": True,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_PEER_REVIEW
        )

    def test_cannot_send_incomplete_request_to_peer_review(self):
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request(
            data=self.get_form_data(with_docs=False)
        )
        self.assertEqual(spending_request.status, SpendingRequest.Status.DRAFT)
        self.assertFalse(spending_request.ready_for_review)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request.pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.content)

    def test_cannot_send_incomplete_request_to_admin_review(self):
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request(
            data=self.get_form_data(with_docs=True)
        )
        self.assertEqual(spending_request.status, SpendingRequest.Status.DRAFT)
        self.assertTrue(spending_request.ready_for_review)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request.pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        spending_request.documents.update(deleted=True)
        spending_request.refresh_from_db()
        self.assertFalse(spending_request.ready_for_review)
        self.client.force_login(self.another_group_finance_admin.role)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request.pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.content)

    def test_cannot_send_request_to_admin_review_without_fund(self):
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request(
            data=self.get_form_data(with_docs=True)
        )
        self.assertEqual(spending_request.status, SpendingRequest.Status.DRAFT)
        self.assertTrue(spending_request.ready_for_review)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request.pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        spending_request.amount = 99999999
        spending_request.save()
        self.assertFalse(spending_request.ready_for_review)
        self.client.force_login(self.another_group_finance_admin.role)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request.pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.content)

    def test_cannot_send_own_request_to_admin_review(self):
        self.client.force_login(self.group_finance_admin.role)
        spending_request = self.create_spending_request()
        self.assertEqual(spending_request.status, SpendingRequest.Status.DRAFT)
        self.assertTrue(spending_request.ready_for_review)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request.pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_PEER_REVIEW
        )
        self.assertTrue(spending_request.ready_for_review)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request.pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.content)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_PEER_REVIEW
        )

    def test_treasurer_can_validate_without_funds(self):
        """Un membre de l'équipe de suivi peut valider une demande même sans fonds"""
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )
        spending_request = self.create_spending_request(without_funds=True)
        spending_request.status = SpendingRequest.Status.AWAITING_ADMIN_REVIEW
        spending_request.save()

        res = self.client.get(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            ),
            data={"comment": "C'est bon !", "status": SpendingRequest.Status.VALIDATED},
            format="multipart",
        )
        self.assertRedirects(res, reverse("admin:donations_spendingrequest_changelist"))

        spending_request.refresh_from_db()
        self.assertEqual(spending_request.status, SpendingRequest.Status.VALIDATED)

    def test_treasurer_can_validate_with_funds(self):
        """Un membre de l'équipe de suivi peut valider une demande même sans fonds"""
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )

        # devrait être assez, en comptant celle de 1000 déjà existante
        AccountOperation.objects.create(
            amount=8000,
            source="revenu:dons",
            destination=f"actif:groupe:{self.group.id}",
        )

        spending_request = self.create_spending_request()
        spending_request.status = SpendingRequest.Status.AWAITING_ADMIN_REVIEW
        spending_request.save()

        res = self.client.get(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request.id,)
            ),
            data={"comment": "C'est bon !", "status": SpendingRequest.Status.VALIDATED},
            format="multipart",
        )
        self.assertRedirects(res, reverse("admin:donations_spendingrequest_changelist"))

        spending_request.refresh_from_db()
        self.assertEqual(spending_request.status, SpendingRequest.Status.TO_PAY)

        operation = spending_request.account_operation
        self.assertIsNotNone(operation)
        self.assertEqual(operation.source, f"actif:groupe:{self.group.id}")
        self.assertEqual(operation.amount, 8500)

    def test_history_is_correct(self):
        """L'historique d'une demande de dépense est correctement généré"""
        self.maxDiff = None

        self.client.force_login(self.group_finance_admin.role)

        # création
        spending_request = self.create_spending_request()
        spending_request_pk = spending_request.pk

        # modification d'un champ
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request_pk,),
            ),
            data={
                "explanation": "C'est vachement important",
                "comment": "J'ai renforcé mon explication !",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # première validation
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request_pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_PEER_REVIEW
        )

        # seconde validation
        self.client.force_login(self.another_group_finance_admin.role)
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request_pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_ADMIN_REVIEW
        )

        # ajout d'un document oublié ==> retour à l'étape de validation
        self.client.force_login(self.group_finance_admin.role)
        file = SimpleUploadedFile(
            "document.pdf",
            b"Un faux fichier",
            content_type="application/pdf",
        )
        res = self.client.post(
            reverse(
                "api_spending_request_document_create", args=(spending_request.pk,)
            ),
            data={
                "title": "Mon super fichier",
                "type": Document.Type.INVOICE,
                "file": file,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status,
            SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION,
        )

        # renvoi vers l'équipe de suivi
        res = self.client.get(
            reverse(
                "api_spending_request_apply_next_status", args=(spending_request_pk,)
            ),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_ADMIN_REVIEW
        )

        # demande d'informations supplémentaires
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )
        _res = self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request_pk,)
            ),
            data={
                "comment": "Le montant ne correspond pas à la facture !",
                "status": SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION,
            },
            format="multipart",
        )
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status,
            SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION,
        )

        # modification de la demande et renvoi vers l'équipe de suivi
        self.client.force_login(self.group_finance_admin.role)
        res = self.client.patch(
            reverse(
                "api_spending_request_retrieve_update_delete",
                args=(spending_request_pk,),
            ),
            data={
                "amount": 8400,
                "comment": "J'ai corrigé le montant... j'avais mal lu !",
                "shouldValidate": True,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        spending_request.refresh_from_db()
        self.assertEqual(
            spending_request.status, SpendingRequest.Status.AWAITING_ADMIN_REVIEW
        )

        # acceptation
        self.client.force_login(
            self.treasurer.role, backend="agir.people.backend.PersonBackend"
        )
        _res = self.client.post(
            reverse(
                "admin:donations_spendingrequest_review", args=(spending_request_pk,)
            ),
            data={
                "comment": "Tout est parfait !",
                "status": SpendingRequest.Status.VALIDATED,
            },
            format="multipart",
        )
        spending_request.refresh_from_db()
        self.assertEqual(spending_request.status, SpendingRequest.Status.TO_PAY)

        hist = spending_request.get_history()
        for d in hist:
            del d["id"]
            del d["modified"]

        self.assertEqual(
            hist,
            [
                {
                    "title": "Création de la demande",
                    "comment": "",
                    "diff": [],
                    "person": self.group_finance_admin,
                    "status": SpendingRequest.Status.DRAFT.value,
                },
                {
                    "title": "Mise à jour de la demande",
                    "comment": "J'ai renforcé mon explication !",
                    "diff": ["Motif de l'achat"],
                    "person": self.group_finance_admin,
                    "status": SpendingRequest.Status.DRAFT.value,
                },
                {
                    "title": "Validée par l'auteur d'origine",
                    "comment": "",
                    "diff": [],
                    "person": self.group_finance_admin,
                    "from_status": SpendingRequest.Status.DRAFT.value,
                    "status": SpendingRequest.Status.AWAITING_PEER_REVIEW.value,
                },
                {
                    "title": "Validée par un⋅e second⋅e animateur⋅rice",
                    "comment": "",
                    "diff": [],
                    "person": self.another_group_finance_admin,
                    "from_status": SpendingRequest.Status.AWAITING_PEER_REVIEW.value,
                    "status": SpendingRequest.Status.AWAITING_ADMIN_REVIEW.value,
                },
                {
                    "title": "Mise à jour de la demande",
                    "comment": "Ajout d'une pièce-jointe : Mon super fichier",
                    "diff": [],
                    "person": self.group_finance_admin,
                    "status": SpendingRequest.Status.AWAITING_ADMIN_REVIEW.value,
                },
                {
                    "title": "Mise à jour de la demande",
                    "comment": "Mise à jour du statut de la demande après une modification",
                    "diff": [],
                    "person": self.group_finance_admin,
                    "from_status": SpendingRequest.Status.AWAITING_ADMIN_REVIEW.value,
                    "status": SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION.value,
                },
                {
                    "title": "Renvoyée pour validation à l'équipe de suivi des questions financières",
                    "comment": "",
                    "diff": [],
                    "person": self.group_finance_admin,
                    "from_status": SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION.value,
                    "status": SpendingRequest.Status.AWAITING_ADMIN_REVIEW.value,
                },
                {
                    "title": "Informations supplémentaires requises",
                    "comment": "Le montant ne correspond pas à la facture !",
                    "diff": [],
                    "person": "Équipe de suivi",
                    "from_status": SpendingRequest.Status.AWAITING_ADMIN_REVIEW.value,
                    "status": SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION.value,
                },
                {
                    "title": "Mise à jour de la demande",
                    "comment": "J'ai corrigé le montant... j'avais mal lu !",
                    "diff": ["Montant de la dépense"],
                    "person": self.group_finance_admin,
                    "status": SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION.value,
                },
                {
                    "title": "Renvoyée pour validation à l'équipe de suivi des questions financières",
                    "comment": "",
                    "diff": [],
                    "person": self.group_finance_admin,
                    "from_status": SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION.value,
                    "status": SpendingRequest.Status.AWAITING_ADMIN_REVIEW.value,
                },
                {
                    "title": "Demande en attente de règlement",
                    "comment": "Tout est parfait !",
                    "diff": [],
                    "person": "Équipe de suivi",
                    "from_status": SpendingRequest.Status.AWAITING_ADMIN_REVIEW.value,
                    "status": SpendingRequest.Status.TO_PAY.value,
                },
            ],
            hist,
        )
