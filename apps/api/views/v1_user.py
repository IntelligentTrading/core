import ast
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from apps.user.models import User as UserModel

from apps.indicator.models import Price as PriceModel
from settings import TEAM_EMOJIS

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

            if request.POST.get('is_subscribed', 'NA').upper() == "TRUE":
                user.is_subscribed = True
            elif request.POST.get('is_subscribed', 'NA').upper() == "FALSE":
                user.is_subscribed = False

            if request.POST.get('token', None):
                token = request.POST.get('token')
                user.set_subscribe_token(token)

            if request.POST.get('is_muted', 'NA').upper() == "TRUE":
                user.is_muted = True
            elif request.POST.get('is_muted', 'NA').upper() == "FALSE":
                user.is_muted = False

            if request.POST.get('risk', 'NA') in ['low', 'medium', 'high']:
                risk_string = request.POST['risk']
                user.risk = user.get_risk_value(risk_string)
                assert user.risk == user.get_risk_value()

            if request.POST.get('horizon', 'NA') in ['short', 'medium', 'long']:
                horizon_string = request.POST['horizon']
                user.horizon = user.get_horizon_value(horizon_string)
                assert user.horizon == user.get_horizon_value()

            user.save()

            return HttpResponse(json.dumps(user.get_telegram_settings())) # ok

        except Exception as e:
            logger.debug(str(e))
            return HttpResponse(json.dumps({'error':str(e)}), status=500) # server error

    def get(self, request, *args, **kwargs):

        chat_id = request.GET.get('chat_id', "")
        if not len(chat_id):
            return HttpResponse(400)  # request error

        user, u_created = UserModel.objects.get_or_create(telegram_chat_id=chat_id)
        # return HttpResponse(json.dumps(user.get_telegram_settings()))  # ok
        return HttpResponse(json.dumps({}))  # ok


class Users(View):
    def dispatch(self, request, *args, **kwargs):
        return super(Users, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        # Filter for authorized users #

        users = UserModel.objects.filter(subscribed_since__isnull=False, is_muted=False)

        if request.GET.get('beta_token_valid', "NA").upper() == "TRUE":
            users = users.exclude(_beta_subscription_token__exact="")
        if request.GET.get('beta_token_valid', "NA").upper() == "FALSE":
            users = users.filter(_beta_subscription_token__exact="")

        if request.GET.get('is_ITT_team', "NA").upper() == "TRUE":
            users = users.filter(is_ITT_team=True)
        if request.GET.get('is_ITT_team', "NA").upper() == "FALSE":
            users = users.filter(is_ITT_team=False)

        # Filter for user preferences #

        risk_string = request.GET.get('risk', 'all')
        assert risk_string in ['low', 'medium', 'high', 'all']
        if risk_string is not 'all':
            users = users.filter(risk = UserModel.get_risk_value(UserModel, risk_string))

        horizon_string = request.GET.get('horizon', 'all')
        assert horizon_string in ['short', 'medium', 'long', 'all']
        if horizon_string is not 'all':
            users = users.filter(horizon=UserModel.get_horizon_value(UserModel, horizon_string))

        # Filters done, compile chat ids #

        chat_id_list = list(users.values_list('telegram_chat_id', flat=True))
        # return HttpResponse(json.dumps({'chat_ids': chat_id_list}))  # ok
        return HttpResponse(json.dumps({}))  # ok
