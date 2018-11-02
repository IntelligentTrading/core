import json

from rest_framework import serializers

from apps.signal.models import Signal
from apps.indicator.models import AnnPriceClassification, EventsElementary, EventsLogical, PriceHistory, PriceResampl, Rsi, Sma, Volume, Price, Sentiment


# ResampledPrice (model: PriceResampl)
class ResampledPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceResampl
        fields = [
            'source', 'resample_period', 'transaction_currency', 'counter_currency', 'timestamp',\
            'open_price', 'close_price','low_price', 'high_price', 'midpoint_price', 'mean_price',\
            'price_variance', 'price_change_24h', 'open_volume', 'close_volume', 'low_volume','high_volume',
        ]

# Signal
class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = ['id', 'source', 'resample_period', 'transaction_currency', 'counter_currency',\
                    'timestamp', 'signal', 'trend', 'horizon', 'price', 'rsi_value', 'sent_at']

# Rsi
class RsiSerializer(serializers.ModelSerializer):

    relative_strength_fixed = serializers.SerializerMethodField('get_relative_strength')

    # we need this because DRF don't like Nan, Infinity and etc
    def get_relative_strength(self, object):
        rs = object.relative_strength
        try:
            json.dumps(rs, allow_nan=False)
        except Exception:
            rs = str(rs) # represent Nan, Infinity and etc as string
        return rs

    class Meta:
        model = Rsi
        fields = ['source', 'resample_period', 'transaction_currency', 'counter_currency', 'timestamp',\
                    'relative_strength_fixed']

# Rsi
class SmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sma
        fields = ['source', 'resample_period', 'transaction_currency', 'counter_currency',\
                    'timestamp', 'sma_period', 'sma_high_price', 'sma_close_price', 'sma_midpoint_price']

# EventsElementary
class EventsElementarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsElementary
        fields = ['source', 'resample_period', 'transaction_currency', 'counter_currency', 'timestamp',\
                    'event_name', 'event_value', 'event_second_value']

# EventsLogical
class EventsLogicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsLogical
        fields = ['source', 'resample_period', 'transaction_currency', 'counter_currency', 'timestamp',\
                    'event_name', 'event_value']

# Price (model: Price)
class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['source', 'transaction_currency', 'counter_currency', 'timestamp', 'price']

# Volume
class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = ['source', 'transaction_currency', 'counter_currency', 'timestamp', 'volume']

# PriceHistory
class HistoryPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['source', 'transaction_currency', 'counter_currency', 'timestamp', 'open_p', 'high', 'low', 'close', 'volume']

# AnnPriceClassification
class AnnPriceClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnPriceClassification
        fields = ['source', 'counter_currency', 'transaction_currency', 'timestamp', 'resample_period', 'predicted_ahead_for',\
                    'probability_same', 'probability_up', 'probability_down', 'ann_model_id']

# Sentiment
class SentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentiment
        fields = ['sentiment_source', 'topic', 'model', 'positive', 'negative', 'neutral', 'compound', 'timestamp']
