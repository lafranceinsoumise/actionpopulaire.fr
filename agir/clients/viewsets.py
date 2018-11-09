from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from . import serializers
from .scopes import scopes


class ScopeViewSet(ViewSet):
    permission_classes = []

    def list(self, request):
        output_serializer = serializers.ScopeSerializer(scopes, many=True)
        return Response(output_serializer.data)

    def retrieve(self, request, pk=None):
        scope = scopes[[scope.name for scope in scopes].index(pk)]
        output_serializer = serializers.ScopeSerializer(scope)
        return Response(output_serializer.data)
