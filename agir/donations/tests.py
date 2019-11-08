from unittest import mock

import re
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agir.api.redis import using_redislite
from agir.donations.forms import AllocationDonationForm
from agir.donations.spending_requests import history
from agir.donations.apps import DonsConfig
from agir.donations.models import (
    Operation,
    Spending,
    SpendingRequest,
    Document,
    MonthlyAllocation,
)
from agir.donations.tasks import (
    send_donation_email,
    send_monthly_donation_confirmation_email,
)
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.lib.utils import front_url
from agir.payments.actions.payments import (
    complete_payment,
    create_payment,
    notify_status_change,
)
from agir.payments.actions.subscriptions import complete_subscription
from agir.payments.models import Payment, Subscription
from agir.people.models import Person
from agir.system_pay import SystemPayPaymentMode
from .views import (
    notification_listener as donation_notification_listener,
    subscription_notification_listener as monthly_donation_subscription_listener,
)


def round_date_like_reversion(d):
    return d.replace(microsecond=d.microsecond // 1000 * 1000)


class DonationTestMixin:
    def setUp(self):
        self.p1 = Person.objects.create_person("test@test.com")

        self.donation_information_payload = {
            "amount": "20000",
            "group": "",
            "allocation": "0",
            "declaration": "Y",
            "nationality": "FR",
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "06 45 78 98 45",
        }

        self.group = SupportGroup.objects.create(
            name="Groupe", type=SupportGroup.TYPE_LOCAL_GROUP
        )
        self.group.subtypes.set(
            [
                SupportGroupSubtype.objects.create(
                    type=SupportGroup.TYPE_LOCAL_GROUP,
                    label=settings.CERTIFIED_GROUP_SUBTYPES[0],
                )
            ]
        )
        Membership.objects.create(supportgroup=self.group, person=self.p1)


class DonationTestCase(DonationTestMixin, TestCase):
    @mock.patch("agir.donations.views.send_donation_email")
    def test_can_donate_while_logged_in(self, send_donation_email):
        self.client.force_login(self.p1.role)
        amount_url = reverse("donation_amount")
        information_url = reverse("donation_information")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        res = self.client.get(information_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(information_url, self.donation_information_payload)
        # no other payment
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=(payment.pk,)))

        res = self.client.get(reverse("payment_return", args=(payment.pk,)))
        self.assertEqual(res.status_code, 200)

        self.p1.refresh_from_db()

        # assert fields have been saved on model
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
        ]:
            self.assertEqual(getattr(self.p1, f), self.donation_information_payload[f])

        # fake systempay webhook
        complete_payment(payment)
        donation_notification_listener(payment)
        send_donation_email.delay.assert_called_once()

    def test_cannot_donate_without_required_fields(self):
        information_url = reverse("donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        required_fields = [
            "declaration",
            "nationality",
            "first_name",
            "last_name",
            "location_address1",
            "location_zip",
            "location_city",
            "location_country",
        ]

        for f in required_fields:
            d = self.donation_information_payload.copy()
            del d[f]

            res = self.client.post(information_url, d)
            self.assertEqual(
                res.status_code,
                200,
                msg="Should not redirect when field '%s' missing" % f,
            )

    def test_cannot_donate_without_asserting_fiscal_residency_when_foreigner(self):
        self.client.force_login(self.p1.role)

        information_url = reverse("donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        self.donation_information_payload["nationality"] = "ES"

        res = self.client.post(information_url, self.donation_information_payload)
        self.assertEqual(res.status_code, 200)

        self.donation_information_payload["fiscal_resident"] = "Y"
        self.donation_information_payload["location_country"] = "ES"
        res = self.client.post(information_url, self.donation_information_payload)
        self.assertEqual(res.status_code, 200)

        self.donation_information_payload["location_country"] = "FR"
        res = self.client.post(information_url, self.donation_information_payload)
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=[payment.pk]))

    @using_redislite
    def test_create_person_when_using_new_address(self):
        information_url = reverse("donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        self.donation_information_payload["email"] = "test2@test.com"
        res = self.client.post(information_url, self.donation_information_payload)
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=[payment.pk]))

        # simulate correct payment
        complete_payment(payment)
        donation_notification_listener(payment)

        p2 = Person.objects.exclude(pk=self.p1.pk).get()
        # assert fields have been saved on model
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "email",
        ]:
            self.assertEqual(getattr(p2, f), self.donation_information_payload[f])

    def test_cannot_donate_to_uncertified_group(self):
        self.group.subtypes.all().delete()
        self.client.force_login(self.p1.role)
        session = self.client.session

        amount_url = reverse("donation_amount")
        information_url = reverse("donation_information")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {
                "type": AllocationDonationForm.TYPE_SINGLE_TIME,
                "amount": "200",
                "group": str(self.group.pk),
                "allocation": "100",
            },
        )
        self.assertRedirects(res, information_url)

        self.assertEqual(session["_donation_"]["group"], None)

    def test_can_donate_with_allocation(self):
        self.client.force_login(self.p1.role)
        session = self.client.session

        amount_url = reverse("donation_amount")
        information_url = reverse("donation_information")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {
                "type": AllocationDonationForm.TYPE_SINGLE_TIME,
                "amount": "200",
                "group": str(self.group.pk),
                "allocation": "100",
            },
        )
        self.assertRedirects(res, information_url)

        self.assertEqual(session["_donation_"]["group"], str(self.group.pk))

        res = self.client.get(information_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.group.pk)

        res = self.client.post(
            information_url,
            {
                **self.donation_information_payload,
                "group": self.group.pk,
                "allocation": "10000",
            },
        )
        # no other payment
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=(payment.pk,)))

        self.assertIn("allocation", payment.meta)
        self.assertIn("group_id", payment.meta)

        self.assertEqual(payment.meta["allocation"], 10000)
        self.assertEqual(payment.meta["group_id"], str(self.group.pk))

    @using_redislite
    def test_allocation_created_on_payment(self):
        payment = create_payment(
            person=self.p1,
            type=DonsConfig.PAYMENT_TYPE,
            price=10000,
            mode=SystemPayPaymentMode.id,
            meta={"allocation": 10000, "group_id": str(self.group.pk)},
        )

        complete_payment(payment)
        notify_status_change(payment)

        self.assertTrue(Operation.objects.exists())
        operation = Operation.objects.get()

        self.assertEqual(operation.amount, 10000)
        self.assertEqual(operation.group, self.group)


class MonthlyDonationTestCase(DonationTestMixin, TestCase):
    def test_cannot_create_allocations_bigger_than_subscription(self):
        self.subscription = Subscription.objects.create(person=self.p1, price=1000)
        MonthlyAllocation.objects.create(amount=500, subscription=self.subscription)
        with self.assertRaises(IntegrityError):
            MonthlyAllocation.objects.create(
                amount=1000, subscription=self.subscription
            )

    @mock.patch("agir.donations.views.send_donation_email")
    def test_can_subscribe_while_logged_in(self, send_donation_email):
        self.client.force_login(self.p1.role)
        amount_url = reverse("donation_amount")
        information_url = reverse("monthly_donation_information")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {
                "type": AllocationDonationForm.TYPE_MONTHLY,
                "amount": "20000",
                "group": str(self.group.pk),
                "allocation": "10000",
            },
        )
        self.assertRedirects(res, information_url)

        res = self.client.get(information_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "200,00")
        self.assertContains(res, "100,00")

        res = self.client.post(
            information_url,
            {
                **self.donation_information_payload,
                "allocation": 10000,
                "group": str(self.group.pk),
            },
        )
        # no other payment
        subscription = Subscription.objects.last()
        allocation = MonthlyAllocation.objects.last()
        self.assertEqual(allocation.subscription, subscription)
        self.assertEqual(allocation.amount, 10000)
        self.assertEqual(allocation.group, self.group)
        self.assertRedirects(res, reverse("subscription_page", args=(subscription.pk,)))

        self.p1.refresh_from_db()

        # assert fields have been saved on model
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
        ]:
            self.assertEqual(getattr(self.p1, f), self.donation_information_payload[f])

        complete_subscription(subscription)
        monthly_donation_subscription_listener(subscription)
        # fake systempay webhook
        send_donation_email.delay.assert_called_once()

        auto_payment = create_payment(
            person=self.p1,
            type=subscription.type,
            price=subscription.price,
            subscription=subscription,
            status=Payment.STATUS_COMPLETED,
        )

        donation_notification_listener(payment=auto_payment)

        # send_donation_email ne devrait pas être rappelé une nouvelle fois
        send_donation_email.delay.assert_called_once()

        operation = Operation.objects.get()
        self.assertEqual(operation.group, self.group)
        self.assertEqual(operation.amount, 10000)

        # vérifions que c'est idempotent
        donation_notification_listener(payment=auto_payment)
        operation = Operation.objects.get()
        self.assertEqual(operation.group, self.group)
        self.assertEqual(operation.amount, 10000)

    def test_can_also_subscribe_from_profile(self):
        self.client.force_login(self.p1.role)
        profile_payments_page = reverse("view_payments")
        information_url = reverse("monthly_donation_information")

        res = self.client.get(profile_payments_page)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            profile_payments_page,
            {
                "type": AllocationDonationForm.TYPE_MONTHLY,
                "amount": "200",
                "group": str(self.group.pk),
                "allocation": "100",
            },
        )
        self.assertRedirects(res, information_url)

    @mock.patch("agir.donations.views.send_monthly_donation_confirmation_email")
    def test_create_person_when_using_new_address(
        self, mock_send_monthly_donation_confirmation_email
    ):
        information_url = reverse("monthly_donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_MONTHLY, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        self.donation_information_payload["email"] = "test2@test.com"
        res = self.client.post(information_url, self.donation_information_payload)
        self.assertRedirects(res, reverse("monthly_donation_confirmation_email_sent"))
        mock_send_monthly_donation_confirmation_email.delay.assert_called_once()

        task_args, task_kwargs = (
            mock_send_monthly_donation_confirmation_email.delay.call_args
        )

        send_monthly_donation_confirmation_email(*task_args, **task_kwargs)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        confirm_subscription_url = reverse("monthly_donation_confirm")
        m = re.search(rf"{confirm_subscription_url}\?[^\s]+", email.body)
        url_with_params = m.group(0)

        res = self.client.get(url_with_params)
        subscription = Subscription.objects.get()
        self.assertRedirects(res, reverse("subscription_page", args=(subscription.pk,)))

        # simulate correct payment
        complete_subscription(subscription)
        monthly_donation_subscription_listener(subscription)

        p2 = Person.objects.exclude(pk=self.p1.pk).get()
        # assert fields have been saved on model
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "email",
        ]:
            self.assertEqual(getattr(p2, f), self.donation_information_payload[f])


class FinancialTriggersTestCase(TestCase):
    def setUp(self):
        self.group1 = SupportGroup.objects.create(
            name="Groupe 1", type=SupportGroup.TYPE_LOCAL_GROUP
        )

        self.group2 = SupportGroup.objects.create(
            name="Groupe 2", type=SupportGroup.TYPE_LOCAL_GROUP
        )

    def create_payment(self, amount, group=None, allocation=None):
        p = Payment.objects.create(
            status=Payment.STATUS_COMPLETED, price=amount, type="don", mode="system_pay"
        )

        if group is not None:
            Operation.objects.create(
                payment=p, amount=allocation or p.price, group=group
            )

        return p

    def test_can_allocate_less_than_payment(self):
        self.create_payment(1000, group=self.group1)
        self.create_payment(1000, group=self.group2, allocation=500)

    def test_cannot_allocate_more_than_payment(self):
        p = self.create_payment(1000)
        with self.assertRaises(IntegrityError):
            Operation.objects.create(payment=p, group=self.group1, amount=1500)

    def test_cannot_reduce_payment_if_allocated(self):
        p = self.create_payment(1000, group=self.group1, allocation=900)
        with self.assertRaises(IntegrityError):
            p.price = 800
            p.save()

    def test_can_spend_less_than_allocation(self):
        self.create_payment(1000, group=self.group1, allocation=500)
        Spending.objects.create(group=self.group1, amount=-300)

    def test_can_spend_less_than_multiple_allocations(self):
        self.create_payment(1000, group=self.group1, allocation=800)
        self.create_payment(1000, group=self.group1, allocation=800)
        Spending.objects.create(group=self.group1, amount=-1500)

    def test_cannot_spend_more_than_allocation(self):
        self.create_payment(1000, group=self.group1)
        with self.assertRaises(IntegrityError):
            Spending.objects.create(group=self.group1, amount=-1800)

    def test_cannot_spend_allocation_from_other_group(self):
        self.create_payment(1000, group=self.group1)
        with self.assertRaises(IntegrityError):
            Spending.objects.create(group=self.group2, amount=-800)

    def test_cannot_reallocation_operation_if_it_creates_integrity_error(self):
        self.create_payment(1000, group=self.group1)
        o = Operation.objects.get()
        s = Spending.objects.create(group=self.group1, amount=-800)
        with self.assertRaises(IntegrityError):
            o.group = self.group2
            o.save()

    def test_cannot_spend_more_in_several_times(self):
        self.create_payment(1000, group=self.group1, allocation=600)
        self.create_payment(1000, group=self.group1, allocation=600)

        Spending.objects.create(group=self.group1, amount=-500)
        Spending.objects.create(group=self.group1, amount=-500)
        with self.assertRaises(IntegrityError):
            Spending.objects.create(group=self.group1, amount=-500)

    def test_cannot_spend_more_by_modifying_spending(self):
        self.create_payment(1000, group=self.group1, allocation=500)

        s = Spending.objects.create(group=self.group1, amount=-500)

        s.amount = -600
        with self.assertRaises(IntegrityError):
            s.save()

    def test_cannot_spend_more_by_modifying_allocation(self):
        p = self.create_payment(1000, group=self.group1)
        o = Operation.objects.get(payment=p)

        Spending.objects.create(group=self.group1, amount=-800)

        o.amount = 500
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                o.save()

        with self.assertRaises(IntegrityError):
            o.delete()


class SpendingRequestTestCase(TestCase):
    def setUp(self):
        self.p1 = Person.objects.create_person("test1@test.com")
        self.p2 = Person.objects.create_person("test2@test.com")
        self.treasurer = Person.objects.create_superperson(
            "treasurer@example.com", "huhuihui"
        )

        self.certified_subtype = SupportGroupSubtype.objects.create(
            label=settings.CERTIFIED_GROUP_SUBTYPES[0],
            description="Groupe certifié",
            type=SupportGroup.TYPE_LOCAL_GROUP,
        )

        self.group1 = SupportGroup.objects.create(
            name="Groupe 1", type=SupportGroup.TYPE_LOCAL_GROUP
        )
        self.group1.subtypes.add(self.certified_subtype)

        self.membership1 = Membership.objects.create(
            person=self.p1, supportgroup=self.group1, is_manager=True
        )
        self.membership2 = Membership.objects.create(
            person=self.p2, supportgroup=self.group1, is_manager=True
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
            "iban": "FR65 0382 9038 7327 9323 466",
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
        """Peut créer une demande de paiement
        """
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
            list(history(spending_request)),
            [
                {
                    "title": "Création de la demande",
                    "user": self.p1.get_short_name(),
                    "modified": round_date_like_reversion(spending_request.modified),
                    "comment": "Création de la demande de dépense",
                    "diff": [],
                }
            ],
        )

    def test_can_manage_spending_request(self):
        """Peut accéder à la page de gestion d'une demande
        """
        self.client.force_login(self.p1.role)

        spending_request = SpendingRequest.objects.create(
            group=self.group1, **self.spending_request_data
        )

        res = self.client.get(
            reverse("manage_spending_request", args=(spending_request.pk,))
        )
        self.assertEqual(res.status_code, 200)

    def test_can_edit_spending_request(self):
        """Peut modifier une demande de paiment
        """
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
        """Peut ajouter un document justificatif
        """
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
        """Peut modifier un document justificatif
        """
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
        """L"historique est correctement généré
        """
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

        hist = list(history(spending_request))
        for d in hist:
            del d["modified"]

        self.assertEqual(
            hist,
            [
                {
                    "title": "Création de la demande",
                    "user": self.p1.get_short_name(),
                    "comment": "Création de la demande de dépense",
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
