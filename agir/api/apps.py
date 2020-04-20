from django.contrib.admin.apps import AdminConfig


class AdminAppConfig(AdminConfig):
    default_site = "agir.api.admin_site.APIAdminSite"

    def ready(self):
        super(AdminAppConfig, self).ready()

        from . import admin
