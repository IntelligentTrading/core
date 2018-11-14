import time
from apps.sentiment.models.sentiment import Sentiment

def _analyze_sentiment():
    timestamp = time.time() // (1 * 60) * (1 * 60)  # current time rounded to a minute
    Sentiment.compute_all(timestamp)