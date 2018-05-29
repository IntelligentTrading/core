from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.cache import cache

from apps.user.models.user import HORIZON_CHOICES


class Main(View):
    def dispatch(self, request, *args, **kwargs):

        # cache.set('my_key', 'hello, world!', 30) # key, value, seconds to expire
        # cache.get('my_key', 'default_value') # key, value if not found

        return super(Main, self).dispatch(request, *args, **kwargs)

    def get(self, request):

        context = get_stats()

        return render(request, 'main.html', context)


def get_stats():
    from apps.signal.models import Signal
    from datetime import datetime, timedelta

    stats = {}

    # ALL SIGNALS
    stats["signals"] = {}
    stats["signals"]["all"] = {}

    signals_24_hrs = Signal.objects.filter(
                sent_at__isnull=False,
                sent_at__gte=datetime.now()-timedelta(hours=24)
            )
    signals_prev_24_hrs = Signal.objects.filter(
                sent_at__gte=datetime.now() - timedelta(hours=48),
                sent_at__lte=datetime.now() - timedelta(hours=24)
            )

    num_signals_24_hrs = signals_24_hrs.count()
    stats["signals"]["all"]["num_signals_24_hrs"] = num_signals_24_hrs

    num_signals_prev_24_hrs = signals_prev_24_hrs.count()
    # stats["signals"]["all"]["num_signals_prev_24_hrs"] = num_signals_prev_24_hrs

    num_signals_24_hrs_delta = num_signals_24_hrs - num_signals_prev_24_hrs

    if num_signals_prev_24_hrs > 0:
        num_signals_24_hrs_delta_percent = \
            float(num_signals_24_hrs_delta) / num_signals_prev_24_hrs
    else:
        num_signals_24_hrs_delta_percent = 0.0
    stats["signals"]["all"]["num_signals_24_hrs_delta_percent"] = \
        num_signals_24_hrs_delta_percent


    # HORIZONS FOR ALL SIGNALS
    for horizon_tuple in HORIZON_CHOICES:
        model_horizon_value, horizon_string = horizon_tuple

        stats["signals"][horizon_string] = {}

        horizon_signals_24_hrs = signals_24_hrs.filter(horizon=model_horizon_value)
        horizon_signals_prev_24_hrs = signals_prev_24_hrs.filter(horizon=model_horizon_value)

        num_horizon_signals_24_hrs = horizon_signals_24_hrs.count()
        stats["signals"][horizon_string]["num_signals_24_hrs"] = num_horizon_signals_24_hrs

        num_horizon_signals_prev_24_hrs = horizon_signals_prev_24_hrs.count()
        # stats["signals"][horizon_string]["num_signals_prev_24_hrs"] = num_horizon_signals_prev_24_hrs

        num_horizon_signals_24_hrs_delta = num_horizon_signals_24_hrs - num_horizon_signals_prev_24_hrs

        if num_horizon_signals_prev_24_hrs > 0:
            num_horizon_signals_24_hrs_delta_percent = \
                float(num_horizon_signals_24_hrs_delta) / num_horizon_signals_prev_24_hrs
        else:
            num_horizon_signals_24_hrs_delta_percent = 0.0
            stats["signals"][horizon_string]["num_signals_24_hrs_delta_percent"] = \
                num_horizon_signals_24_hrs_delta_percent


    # RSI SIGNALS
    stats["rsi_signals"] = {}
    stats["rsi_signals"]["all"] = {}

    rsi_signals_24_hrs = signals_24_hrs.filter(signal="RSI")
    rsi_signals_prev_24_hrs = signals_prev_24_hrs.filter(signal="RSI")

    num_signals_24_hrs = rsi_signals_24_hrs.count()
    stats["rsi_signals"]["all"]["num_signals_24_hrs"] = num_signals_24_hrs

    num_signals_prev_24_hrs = rsi_signals_prev_24_hrs.count()
    # stats["signals"]["all"]["num_signals_prev_24_hrs"] = num_signals_prev_24_hrs

    num_signals_24_hrs_delta = num_signals_24_hrs - num_signals_prev_24_hrs

    if num_signals_prev_24_hrs > 0:
        num_signals_24_hrs_delta_percent = \
            float(num_signals_24_hrs_delta) / num_signals_prev_24_hrs
    else:
        num_signals_24_hrs_delta_percent = 0.0
    stats["rsi_signals"]["all"]["num_signals_24_hrs_delta_percent"] = \
        num_signals_24_hrs_delta_percent


    # HORIZONS FOR RSI SIGNALS
    for horizon_tuple in HORIZON_CHOICES:
        model_horizon_value, horizon_string = horizon_tuple

        stats["rsi_signals"][horizon_string] = {}

        horizon_signals_24_hrs = rsi_signals_24_hrs.filter(horizon=model_horizon_value)
        horizon_signals_prev_24_hrs = rsi_signals_prev_24_hrs.filter(horizon=model_horizon_value)

        num_horizon_signals_24_hrs = horizon_signals_24_hrs.count()
        stats["rsi_signals"][horizon_string]["num_signals_24_hrs"] = num_horizon_signals_24_hrs

        num_horizon_signals_prev_24_hrs = horizon_signals_prev_24_hrs.count()
        # stats["signals"][horizon_string]["num_signals_prev_24_hrs"] = num_horizon_signals_prev_24_hrs

        num_horizon_signals_24_hrs_delta = num_horizon_signals_24_hrs - num_horizon_signals_prev_24_hrs

        if num_horizon_signals_prev_24_hrs > 0:
            num_horizon_signals_24_hrs_delta_percent = \
                float(num_horizon_signals_24_hrs_delta) / num_horizon_signals_prev_24_hrs
        else:
            num_horizon_signals_24_hrs_delta_percent = 0.0
            stats["rsi_signals"][horizon_string]["num_signals_24_hrs_delta_percent"] = \
                num_horizon_signals_24_hrs_delta_percent


    print(stats)

    return stats
