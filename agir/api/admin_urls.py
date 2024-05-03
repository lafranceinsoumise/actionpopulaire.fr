"""Contient les définitions des URLs utilisées uniquement dans l'admin

Ce fichier est rendu obligatoire par le besoin de pouvoir résoudre des URLs
vers l'admin dans des configurations où ces motifs d'URLs ne sont pas chargés.

Il faut pour cela donner à `reverse` l'argument `urlconf` qui n'accepte PAS
de listes d'URLs, comme celles renvoyées par `admin.site.urls`. Il faut donc
ce fichier intermédiaire, même s'il ne contient pour le moment QUE les URLs
de notre site d'admin.
"""

from django.contrib import admin
from django.urls import path


urlpatterns = (path("admin/", admin.site.urls),)
