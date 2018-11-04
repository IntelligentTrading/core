from rest_framework.generics import ListAPIView

from apps.api.serializers import SentimentSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination

from apps.api.helpers import filter_queryset_by_timestamp
from settings import REDDIT, BITCOINTALK, TWITTER, VADER, NN_SENTIMENT
from apps.indicator.models.sentiment import SUBREDDIT_BTC, SUBREDDIT_CRYPTO, TWITTER_ALT_SEARCH_QUERY, TWITTER_BTC_SEARCH_QUERY, BITCOINTALK_BTC, BITCOINTALK_ALT

from django.shortcuts import render
from apps.indicator.models.sentiment import Sentiment

model_names = {
    VADER: 'vader',
    NN_SENTIMENT: 'lstm'
}

pretty_model_names = {
    VADER: 'Vader rule-based analyzer',
    NN_SENTIMENT: 'LSTM neural network based sentiment analyzer'
}

pretty_topic_names = {
   'BTC' : 'Bitcoin',
   'alt': 'altcoins and general crypto'
}

reddit_url_infos = {
    'BTC': SUBREDDIT_BTC,
    'alt': SUBREDDIT_CRYPTO
}

twitter_url_infos = {
    'BTC': TWITTER_BTC_SEARCH_QUERY,
    'alt': TWITTER_ALT_SEARCH_QUERY
}

bitcointalk_url_infos = {
    'BTC': BITCOINTALK_BTC,
    'alt': BITCOINTALK_ALT
}


class SentimentClassification(ListAPIView):

    permission_classes = (RestAPIPermission,)
    pagination_class = StandardResultsSetPagination
    serializer_class = SentimentSerializer
    filter_fields = ('sentiment_source', 'topic', 'model', 'timestamp')

    model = serializer_class.Meta.model

    def get_queryset(self):
        return filter_queryset_by_timestamp(self)


def _filter_or_none(sentiment_source, topic, model, from_comments):
    result = Sentiment.objects.filter(sentiment_source=sentiment_source, model=model, topic=topic,
                                      from_comments=from_comments).order_by('-timestamp')
    if result.exists():
        return result[:1][0]
    else:
        return None


def _create_sentiment_result_dict(topic, model):
    return {
        'reddit':
            _filter_or_none(sentiment_source=REDDIT, model=model, topic=topic, from_comments=False),
        'bitcointalk':
            _filter_or_none(sentiment_source=BITCOINTALK, model=model, topic=topic, from_comments=False),
        'twitter':
            _filter_or_none(sentiment_source=TWITTER, model=model, topic=topic, from_comments=False),
        'reddit_comments':
            _filter_or_none(sentiment_source=REDDIT, model=model, topic=topic, from_comments=True),
        'bitcointalk_comments':
            _filter_or_none(sentiment_source=BITCOINTALK, model=model, topic=topic, from_comments=True),
        'name': f'{pretty_model_names[model]}, topic of interest: {pretty_topic_names[topic]}',
        'reddit_url_info': reddit_url_infos[topic],
        'bitcointalk_url_info': bitcointalk_url_infos[topic],
        'twitter_url_info': twitter_url_infos[topic]
    }


def sentiment_index(request):
    topics = ['BTC', 'alt']
    models = [VADER, NN_SENTIMENT]
    results = {}


    for topic in topics:
        for model in models:
            key = f'{topic.lower()}_{model_names[model]}'
            results[key] = _create_sentiment_result_dict(topic, model)


    """

    results = {
        latest_data = Sentiment.objects.filter(sentiment_source=REDDIT, model=VADER, topic='BTC').order_by('-timestamp')[:1]
        'btc_vader': {
            'reddit': Sentiment.objects.filter(sentiment_source=REDDIT, model=VADER, topic='BTC').order_by('-timestamp')[:1][0],
            'bitcointalk': latest_data[0],
            'twitter': latest_data[0],
        }
    }

    print(results)
    # context = {'btc_reddit': latest_data[0]}
    """

    context = {
        'result_data': results,
    }

    return render(request, 'sentiment_index.html', context)