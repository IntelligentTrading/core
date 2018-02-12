from rest_framework.generics import ListAPIView

from apps.api.serializers.signal import SignalSerializer
from apps.api.permissions import RestAPIPermission

from apps.signal.models import Signal

class SignalListAPIView(ListAPIView):
    queryset = Signal.objects.order_by('-id') # last signal will be on top/first
    permission_classes = (RestAPIPermission, )
    serializer_class = SignalSerializer
