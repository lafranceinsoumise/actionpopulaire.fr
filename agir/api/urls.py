"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.urls import path, include
from django_prometheus.exports import ExportToDjangoView as metric_view

from agir.lib.http import with_http_basic_auth
from . import settings
from agir.front.views import NotFoundView

handler404 = NotFoundView.as_view()

if not settings.ENABLE_FRONT:
    handler404 = "agir.api.admin_views.page_not_found_view"

urlpatterns = [
    path("nuntius/", include("nuntius.urls")),
    path("webhooks/", include("agir.webhooks.urls")),
    path("anymail/", include("anymail.urls")),
    path(
        "metrics/",
        with_http_basic_auth({settings.PROMETHEUS_USER: settings.PROMETHEUS_PASSWORD})(
            metric_view
        ),
    ),
]

if settings.ENABLE_ADMIN:
    urlpatterns.append(path("", include("agir.api.admin_urls")))

if settings.ENABLE_API:
    urlpatterns.append(path("legacy/", include("agir.api.routers")))

if settings.ENABLE_FRONT:
    urlpatterns += [path("", include("agir.api.front_urls"))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns

urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
