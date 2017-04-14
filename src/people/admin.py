from django.contrib import admin

from .models import Person, PersonTag


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonTag)
class PersonTagAdmin(admin.ModelAdmin):
    pass
