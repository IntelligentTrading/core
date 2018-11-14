from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from settings import SENTIMENT_SOURCE_CHOICES,SENTIMENT_MODEL_CHOICES, REDDIT, TWITTER, BITCOINTALK, NN_SENTIMENT, VADER
import logging
from settings import MODIFY_DB
from apps.sentiment.models.sentiment_analysis import Subreddit, Twitter, Bitcointalk, LSTMSentimentAnalyzer, VaderSentimentAnalyzer
import numpy as np

SUBREDDIT_BTC = 'BTC'
SUBREDDIT_CRYPTO = 'CryptoCurrency'
MAX_TOPICS = 10
BITCOINTALK_BTC = 'https://bitcointalk.org/index.php?board=1.0;sort=last_post;desc'
BITCOINTALK_ALT = 'https://bitcointalk.org/index.php?board=67.0;sort=last_post;desc'
TWITTER_BTC_SEARCH_QUERY = 'btc'
TWITTER_ALT_SEARCH_QUERY = 'crypto'
NUM_TWEETS = 10

logger = logging.getLogger(__name__)

class Sentiment(models.Model):
    sentiment_source = models.SmallIntegerField(choices=SENTIMENT_SOURCE_CHOICES, null=False)
    topic = models.CharField(max_length=6, null=False, blank=False)
    model = models.SmallIntegerField(choices=SENTIMENT_MODEL_CHOICES, null=False)
    positive = models.FloatField(null=False)
    negative = models.FloatField(null=False)
    neutral = models.FloatField(null=True)
    compound = models.FloatField(null=True)
    timestamp = UnixTimeStampField(null=False)
    from_comments = models.BooleanField(null=False)


    # INDEX
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'model', 'sentiment_source', 'topic']),
        ]

    def _compute(self, timestamp, analyzer, analyzer_code, sentiment_source_code, topic, from_comments):

        if not from_comments:
            score = analyzer.calculate_current_mean_headline_sentiment()
        else:
            score = analyzer.calculate_current_mean_topic_sentiment()

        self.sentiment_source = sentiment_source_code
        self.topic = topic
        self.model = analyzer_code
        self.positive = score.positive
        self.neutral = score.neutral if not np.isnan(score.neutral) else None
        self.negative = score.negative
        self.compound = score.compound if not np.isnan(score.neutral) else None
        self.timestamp = timestamp
        self.from_comments = from_comments\


    @staticmethod
    def _create_instance_and_write(timestamp, analyzer, analyzer_code, sentiment_source_code, topic, from_comments):
        sentiment_instance = Sentiment()
        sentiment_instance._compute(timestamp, analyzer, analyzer_code, sentiment_source_code, topic, from_comments)
        if MODIFY_DB:
            sentiment_instance.save()

    @staticmethod
    def _go_through_source(timestamp, sentiment_data_source, sentiment_data_source_code, topic, include_comments):
        lstm_analyzer = LSTMSentimentAnalyzer(sentiment_data_source)
        Sentiment._create_instance_and_write(
            timestamp, lstm_analyzer, NN_SENTIMENT, sentiment_data_source_code, topic, False
        )

        vader_analyzer = VaderSentimentAnalyzer(sentiment_data_source)
        Sentiment._create_instance_and_write(
            timestamp, vader_analyzer, VADER, sentiment_data_source_code, topic, False
        )

        if include_comments:
            lstm_analyzer = LSTMSentimentAnalyzer(sentiment_data_source)
            Sentiment._create_instance_and_write(
                timestamp, lstm_analyzer, NN_SENTIMENT, sentiment_data_source_code, topic, True
            )

            vader_analyzer = VaderSentimentAnalyzer(sentiment_data_source)
            Sentiment._create_instance_and_write(
                timestamp, vader_analyzer, VADER, sentiment_data_source_code, topic, True
            )



    @staticmethod
    def compute_all(timestamp):
        try:
            # go through Reddit
            logging.info(' >>>>>> Processing Reddit sentiment...')
            subreddit = Subreddit(SUBREDDIT_BTC, max_topics=MAX_TOPICS)
            Sentiment._go_through_source(timestamp, subreddit, REDDIT, 'BTC', True)

            subreddit = Subreddit(SUBREDDIT_CRYPTO, max_topics=MAX_TOPICS)
            Sentiment._go_through_source(timestamp, subreddit, REDDIT, 'alt', True)
        except Exception as e:
            logging.error(f'Unable to go through Reddit: {str(e)}')

        try:
            logging.info('>>>>> Processing Bitcointalk sentiment...')
            # go through Bitcointalk
            bitcointalk = Bitcointalk(BITCOINTALK_BTC)
            Sentiment._go_through_source(timestamp, bitcointalk, BITCOINTALK, 'BTC', True)

            bitcointalk = Bitcointalk(BITCOINTALK_ALT)
            Sentiment._go_through_source(timestamp, bitcointalk, BITCOINTALK, 'alt', True)
        except Exception as e:
            logging.error(f'Unable to go through Bitcointalk: {str(e)}')

        try:
            logging.info('>>>>> Processing Twitter sentiment...')
            # go through Twitter
            twitter = Twitter(TWITTER_BTC_SEARCH_QUERY, NUM_TWEETS)
            Sentiment._go_through_source(timestamp, twitter, TWITTER, 'BTC', False)

            twitter = Twitter(TWITTER_ALT_SEARCH_QUERY, NUM_TWEETS)
            Sentiment._go_through_source(timestamp, twitter, TWITTER, 'alt', False)
        except Exception as e:
            logging.error(f'Unable to go through Twitter: {str(e)}')


        logger.info("   ...All sentiment calculations have been done and saved.")
