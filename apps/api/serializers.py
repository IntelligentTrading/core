from rest_framework import serializers

from apps.signal.models import Signal
from apps.indicator.models import Price, Volume, Rsi

# Signal
class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = ['timestamp', 'transaction_currency', 'counter_currency', 'signal', 'trend', 'horizon', 'price', 'rsi_value']

# Price
class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['source', 'transaction_currency', 'counter_currency', 'price', 'timestamp']

# Volume
class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = ['source', 'transaction_currency', 'counter_currency', 'volume', 'timestamp']

# Rsi
class RsiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rsi
        fields = ['timestamp', 'source', 'counter_currency', 'transaction_currency', 'resample_period', 'relative_strength']

# PriceResampled