import json

from rest_framework import serializers

from apps.signal.models import Signal
from apps.indicator.models import Price
from apps.indicator.models import PriceResampl, Volume, Rsi, EventsElementary


# Signal
class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = ['timestamp', 'transaction_currency', 'counter_currency', 'signal', 'trend', 'horizon', 'price', 'rsi_value']

# Price (model: PriceResampl)
class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceResampl
        fields = [
            'timestamp', 'source', 'counter_currency', 'transaction_currency', 'resample_period',\
            'open_price', 'close_price','low_price', 'high_price', 'midpoint_price', 'mean_price',\
            'price_variance',
        ]

# Volume
class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = ['timestamp', 'source', 'transaction_currency', 'counter_currency', 'volume']

# Rsi
class RsiSerializer(serializers.ModelSerializer):

    relative_strength_fixed = serializers.SerializerMethodField('get_relative_strength')

    def get_relative_strength(self, object):
        rs = object.relative_strength
        try:
            json.dumps(rs, allow_nan=False)
        except Exception:
            rs = str(rs) # represent Nan, Infinity and etc as string
        return rs

    class Meta:
        model = Rsi
        fields = ['timestamp', 'source', 'counter_currency', 'transaction_currency', \
                    'resample_period', 'relative_strength_fixed']

# EventsElementary
class EventsElementarySerializer(serializers.ModelSerializer):

    class Meta:
        model = EventsElementary
        fields = ['timestamp', 'source', 'counter_currency', 'transaction_currency', \
                    'resample_period', 'event_name', 'event_value', 'event_second_value']

