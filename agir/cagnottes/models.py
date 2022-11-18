from django.db import models


class Cagnotte(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField()
    public = models.BooleanField(null=False, default=True)
