from django.http import HttpResponseRedirect
from django.urls import reverse


class InsoumiseOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.person.is_insoumise == False:
            return HttpResponseRedirect(reverse("become_insoumise"))
        return super().dispatch(request, *args, **kwargs)
