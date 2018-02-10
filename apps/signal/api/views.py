from rest_framework.generics import ListAPIView

from .serializers import SignalSerializer
from .permissions import RestAPIPermission

from ..models import Signal

class SignalListAPIView(ListAPIView):
    queryset = Signal.objects.order_by('-id') # last signal will be on top/first
    permission_classes = (RestAPIPermission, )
    serializer_class = SignalSerializer
