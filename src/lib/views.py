from rest_framework.generics import GenericAPIView, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, ValidationError


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
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        try:
            obj = queryset.get(**{self.lookup_field: self.kwargs[lookup_url_kwarg]})
        except (ObjectDoesNotExist, ValidationError, TypeError, ValueError):
            obj = get_object_or_404(queryset, nb_id=self.kwargs[lookup_url_kwarg])

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class CreationSerializerMixin(object):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.creation_serializer_class
        return self.serializer_class
