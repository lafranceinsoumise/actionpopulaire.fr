"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from ajax_select import urls as ajax_select_urls
from . import routers, admin, settings

import front.urls
import webhooks.urls

urlpatterns = [
    url(r'^admin/', include('admin_steroids.urls')),
    url(r'^admin/', admin.admin_site.urls),
    url(r'^webhooks/', include(webhooks.urls)),
    url(r'^ajax_select/', include(ajax_select_urls)),
]

if settings.DEBUG or settings.ENABLE_API:
    urlpatterns.append(
        url(r'^legacy/', include(routers.legacy_api.urls, namespace='legacy'))
    )

if settings.DEBUG or settings.ENABLE_FRONT:
    urlpatterns.append(
        url(r'^', include(front.urls))
    )


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
