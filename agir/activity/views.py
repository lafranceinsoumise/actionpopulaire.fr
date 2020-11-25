from rest_framework.generics import RetrieveUpdateAPIView

from agir.activity.models import Activity
from agir.activity.serializers import ActivitySerializer
from agir.lib.rest_framework_permissions import GlobalOrObjectPermissions


class ActivityAPIView(RetrieveUpdateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (GlobalOrObjectPermissions,)
