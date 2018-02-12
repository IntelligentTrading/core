from rest_framework import serializers

from ..models import Signal

class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = ['timestamp', 'transaction_currency', 'counter_currency', 'signal', 'trend', 'horizon', 'price', 'rsi_value']
