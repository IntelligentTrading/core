from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView
)

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models import Signal

from .serializers import SignalSerializer

class SignalListAPIView(ListAPIView):
    queryset = Signal.objects.order_by('-id') # last signal will be on top/first
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = SignalSerializer
