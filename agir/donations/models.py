from django.db import models
from django.utils.translation import ugettext_lazy as _


class Operation(models.Model):
    STATUS_COMPLETE = "C"
    STATUS_PENDING_VALIDATION = "P"
    STATUS_CHOICES = (
        (STATUS_COMPLETE, "Opération terminée"),
        (STATUS_PENDING_VALIDATION, "Opération en attente de validation"),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    group = models.ForeignKey(
        to="groups.SupportGroup",
        null=False,
        editable=False,
        blank=False,
        on_delete=models.PROTECT,
    )
    amount = models.IntegerField(
        _("opération en centimes d'euros"), null=False, blank=False, editable=False
    )
    payment = models.OneToOneField(
        to="payments.Payment",
        null=True,
        editable=False,
        blank=True,
        on_delete=models.PROTECT,
    )


class Spending(Operation):
    """
    Utility class to use when playing with spending operations.
    """

    def save(self, *args, **kwargs):
        if self.amount > 0:
            raise Exception("Spendings must be negative")

        super().save(*args, **kwargs)

    class Meta:
        proxy = True
