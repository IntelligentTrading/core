import json
import logging
from copy import deepcopy
from datetime import datetime, timedelta

from cache_memoize import cache_memoize
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import RestAPIPermission
from apps.signal.models import Signal
from apps.user.models.user import SHORT_HORIZON, MEDIUM_HORIZON, LONG_HORIZON
from settings import BINANCE


class Portfolio(APIView):
    permission_classes = (RestAPIPermission,)

    def get(self, request, format=None):
        return Response(get_reccomended_allocations())


@cache_memoize(60 * 10)
def get_reccomended_allocations():
    now_datetime = datetime.now()
    period_1hr_seconds = timedelta(hours=1)
    BTC_minimum_reserve = 0.0010
    BNB_minimum_reserve = 0.0005

    horizon_periods = {
        SHORT_HORIZON: 1,
        MEDIUM_HORIZON: 6,
        LONG_HORIZON: 24,
    }

    horizon_life_spans = {
        SHORT_HORIZON: 6,
        MEDIUM_HORIZON: 6,
        LONG_HORIZON: 6,
    }

    horizon_weights = {
        SHORT_HORIZON: 1,
        MEDIUM_HORIZON: 1,
        LONG_HORIZON: 1,
    }

    horizon_signals = {}
    for horizon in [SHORT_HORIZON, MEDIUM_HORIZON, LONG_HORIZON]:
        horizon_signals[horizon] = Signal.objects.filter(
            timestamp__gte=(
                    now_datetime - (period_1hr_seconds * horizon_periods[horizon]) * horizon_life_spans[horizon]
            ),
            horizon=horizon, source=BINANCE
        )
    all_signals = horizon_signals[SHORT_HORIZON] | horizon_signals[MEDIUM_HORIZON] | horizon_signals[LONG_HORIZON]

    tickers_dict = {
        "BTC_USDT": {
            "coin": "BTC",
            "vote": 0,
            "portion": BTC_minimum_reserve,  # hold by default
        },
        "BNB_BTC": {
            "coin": "BNB",
            "vote": 0,
            "portion": BNB_minimum_reserve,  # hold by default
        }
    }

    for signal in all_signals:
        ticker = f"{signal.transaction_currency}_{signal.get_counter_currency_display()}"

        if ticker not in tickers_dict:
            tickers_dict[ticker] = {
                "coin": str(signal.transaction_currency),
                "vote": 0,
                "portion": 0,
            }

        time_weight = float(1) - (
                (now_datetime - signal.timestamp).total_seconds() /
                (period_1hr_seconds * horizon_periods[signal.horizon] * horizon_life_spans[
                    signal.horizon]).total_seconds()
        )
        vote = float(signal.trend) * horizon_weights[signal.horizon] * time_weight
        tickers_dict[ticker]["vote"] += vote

    # Remove tickers with net-negative votes
    for ticker, data in deepcopy(tickers_dict).items():
        if data["vote"] <= 0.01:
            del tickers_dict[ticker]

    votes_sum = sum([data["vote"] for ticker, data in tickers_dict.items()])
    logging.debug("SUM of votes: " + str(votes_sum))

    for ticker, data in deepcopy(tickers_dict).items():
        tickers_dict[ticker]["portion"] = (data["vote"] / votes_sum) // 0.0001 / 10000
        if tickers_dict[ticker]["portion"] < 0.0001:
            del tickers_dict[ticker]

    allocations_sum = sum([data["portion"] for ticker, data in tickers_dict.items()])
    logging.debug(f"preliminary SUM of allocations: {round(allocations_sum*100,3)}%")

    allocations_dict = {}
    for ticker, data in tickers_dict.items():
        if not data["coin"] in allocations_dict:
            allocations_dict[data["coin"]] = 0
        allocations_dict[data["coin"]] += data["portion"]

    allocations_dict["BNB"] = max([BNB_minimum_reserve, allocations_dict["BNB"]])
    allocations_dict["BTC"] = max(
        [BTC_minimum_reserve, (0.9999 - BNB_minimum_reserve - allocations_sum + allocations_dict["BTC"])])

    allocations_list = [{"coin": coin, "portion": (portion // 0.0001 / 10000)} for coin, portion in
                        allocations_dict.items()]
    allocations_sum = sum([a["portion"] for a in allocations_list])

    logging.debug(f"SUM of allocations: {round(allocations_sum*100,3)}%")
    logging.debug(json.dumps(allocations_list))
    return allocations_list
