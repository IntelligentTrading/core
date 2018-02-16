from rest_framework import serializers

from apps.signal.models import Signal
from apps.indicator.models import PriceResampl, Volume, Rsi

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
            'price_variance'
        ]

# Volume
class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = ['timestamp', 'source', 'transaction_currency', 'counter_currency', 'volume']

# Rsi
class RsiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rsi
        fields = ['timestamp', 'source', 'counter_currency', 'transaction_currency', 'resample_period', 'relative_strength']
