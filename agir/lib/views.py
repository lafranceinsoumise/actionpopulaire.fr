from datetime import datetime

import pytz
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic.edit import FormMixin
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.views import APIView

PICT_RATIO_MIN = 1.8
PICT_RATIO_MAX = 2.1


class NationBuilderViewMixin(GenericAPIView):
    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        try:
            obj = queryset.get(**{self.lookup_field: self.kwargs[lookup_url_kwarg]})
        except (ObjectDoesNotExist, ValidationError, TypeError, ValueError):
            obj = get_object_or_404(queryset, nb_id=self.kwargs[lookup_url_kwarg])

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class ImageSizeWarningMixin(FormMixin, View):
    """Affiche un message d'avertissement lors d'un upload d'image mal dimensionné.

    Cette mixin fonctionne avec sur un champ de model de type StdImageField dont on renseigne
    le nom dans l'attribut de view `image_field`
    """

    image_field = None

    def form_valid(self, form):
        image = form.cleaned_data[self.image_field]
        if hasattr(image, "image"):
            size = image.image.size
            if size[1] == 0:
                return super().form_valid(form)
            ratio = size[0] / size[1]
            if not (PICT_RATIO_MIN <= ratio <= PICT_RATIO_MAX):
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    "Attention, les dimensions de l'image ne sont pas adaptées aux réseaux sociaux. "
                    "L'image sera alors tronquée lors du partage. "
                    f"Le ratio de {image.name} est de {round(ratio, 2)}:1. "
                    f"La dimension optimale est 2:1. (deux fois plus large que haut)",
                )
        return super().form_valid(form)


class IframableMixin(View):
    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        if request.GET.get("iframe"):
            res.xframe_options_exempt = True
        return res


class AnonymousAPIView(APIView):
    def perform_authentication(self, request):
        # original implementation only access request.user to force authentication
        # we pass so it is done lazyly instead
        pass
