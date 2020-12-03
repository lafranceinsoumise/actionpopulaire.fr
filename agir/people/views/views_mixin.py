from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse


class InsoumiseOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.person.is_insoumise:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)
