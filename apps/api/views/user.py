import ast
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from apps.user.models import User as UserModel

from apps.indicator.models import Price as PriceModel

logger = logging.getLogger(__name__)

class User(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(User, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            chat_id = request.POST.get('chat_id', "")
            if not len(chat_id):
                return HttpResponse(400)  # request error
            user, u_created = UserModel.objects.get_or_create(telegram_chat_id=chat_id)

            if request.POST.get('is_subscribed', 'n/a') in ["True", "False"]:
                user.is_subscribed = ast.literal_eval(request.POST['is_subscribed'])

            if request.POST.get('is_muted', 'n/a') in ["True", "False"]:
                user.is_muted = ast.literal_eval(request.POST['is_muted'])

            if request.POST.get('risk', 'n/a') in ['low', 'medium', 'high']:
                risk_string = request.POST['risk']
                if risk_string == 'low':
                    user.risk = UserModel.LOW_RISK
                elif risk_string == 'medium':
                    user.risk = UserModel.MEDIUM_RISK
                elif risk_string == 'high':
                    user.risk = UserModel.HIGH_RISK

            if request.POST.get('horizon', 'n/a') in ['short', 'medium', 'long']:
                horizon_string = request.POST['horizon']
                if horizon_string == 'short':
                    user.horizon = UserModel.SHORT_HORIZON
                elif horizon_string == 'medium':
                    user.horizon = UserModel.MEDIUM_HORIZON
                elif horizon_string == 'long':
                    user.horizon = UserModel.LONG_HORIZON

            user.save()

            return HttpResponse(json.dumps(user.get_telegram_settings())) # ok

        except Exception as e:
            logger.debug(str(e))
            return HttpResponse(json.dumps({'error':str(e)}), status=500) # server error

    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps({'error':'POST requests only'}))  # ok
