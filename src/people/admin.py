from django.contrib import admin
from api.admin import admin_site

from .models import Person, PersonTag


@admin.register(Person, site=admin_site)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonTag, site=admin_site)
class PersonTagAdmin(admin.ModelAdmin):
    pass
