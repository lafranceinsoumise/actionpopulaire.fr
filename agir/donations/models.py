from django.db import models
from django.utils.translation import ugettext_lazy as _


class DonationAllocation(models.Model):
    payment = models.OneToOneField(to='payments.Payment', null=False, editable=False, on_delete=models.CASCADE)
    group = models.ForeignKey(to='groups.SupportGroup', null=False, editable=False, blank=False, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(_("allocation en centimes d'euros"), null=False, blank=False, editable=False)


class Spending(models.Model):
    group = models.ForeignKey(to='groups.SupportGroup', null=False, editable=False, blank=False, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(_("dépense en centimes d'euros"), null=False, blank=False, editable=False)

