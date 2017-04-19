from django.contrib import admin

from . import models

@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Scope)
class ScopeAdmin(admin.ModelAdmin):
    pass
