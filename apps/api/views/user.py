import logging
from django.http import HttpResponse
from django.views.generic import View

from apps.indicator.models import Price as PriceModel

logger = logging.getLogger(__name__)

class User(View):
    def dispatch(self, request, *args, **kwargs):
        return super(User, self).dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        try:
            chat_id = request.POST.get('chat_id', None)
            is_subscribed = request.POST.get('is_subscribed', None)
            is_muted = request.POST.get('is_muted', None)

            assert len(chat_id)
            user, u_created = User.objects.get_or_create(chat_id=chat_id)

            user.is_subscribed = user.is_subscribed if is_subscribed == None else is_subscribed
            user.is_muted = user.is_muted if is_muted == None else is_muted

            return HttpResponse(200) # ok

        except Exception as e:
            logger.debug(str(e))
            return HttpResponse(500) # server error
