from django.shortcuts import render
from django.views.generic import View

from apps.user.models.user import HORIZON_CHOICES


class Main(View):
    def dispatch(self, request, *args, **kwargs):

        # cache.set('my_key', 'hello, world!', 30) # key, value, seconds to expire
        # cache.get('my_key', 'default_value') # key, value if not found

        return super(Main, self).dispatch(request, *args, **kwargs)

    def get(self, request):

        context = {
            "signals": getSignalStats()
        }
        # print(context["signals"])
        return render(request, 'main.html', context)


def getSignalStats():
    from apps.signal.models import Signal
    from datetime import datetime, timedelta

    stats = {}

    # ALL SIGNALS
    signals_24_hrs = Signal.objects.filter(
                sent_at__isnull=False,
                sent_at__gte=datetime.now()-timedelta(hours=24)
            )
    signals_prev_24_hrs = Signal.objects.filter(
                sent_at__gte=datetime.now() - timedelta(hours=48),
                sent_at__lte=datetime.now() - timedelta(hours=24)
            )


    # ADD FOR EACH SIGNAL TYPE
    for signal_name in ["total", "RSI_Cumulative", "RSI", "SMA", "ANN_Simple",]:

        if signal_name is "total":
            subset_signals_24_hrs = signals_24_hrs
            subset_signals_prev_24_hrs = signals_prev_24_hrs
        else:
            subset_signals_24_hrs = signals_24_hrs.filter(signal=signal_name)
            subset_signals_prev_24_hrs = signals_prev_24_hrs.filter(signal=signal_name)

        stats[signal_name] = {}
        stats[signal_name]["all"] = {}
        stats[signal_name]["all"]["num_signals_24_hrs"] = subset_signals_24_hrs.count()
        stats[signal_name]["all"]["num_signals_prev_24_hrs"] = subset_signals_prev_24_hrs.count()

        num_signals_24_hrs_delta = stats[signal_name]["all"]["num_signals_24_hrs"] - stats[signal_name]["all"]["num_signals_prev_24_hrs"]
        if stats[signal_name]["all"]["num_signals_prev_24_hrs"] > 0:
            num_signals_24_hrs_delta_percent = \
                float(num_signals_24_hrs_delta) / stats[signal_name]["all"]["num_signals_prev_24_hrs"]
        else:
            num_signals_24_hrs_delta_percent = 0.0
        stats[signal_name]["all"]["num_signals_24_hrs_delta_percent"] = num_signals_24_hrs_delta_percent

        # ADD HORIZONS
        for horizon_tuple in HORIZON_CHOICES:
            model_horizon_value, horizon_string = horizon_tuple

            stats[signal_name][horizon_string] = {}

            horizon_signals_24_hrs = subset_signals_24_hrs.filter(horizon=model_horizon_value)
            horizon_signals_prev_24_hrs = subset_signals_prev_24_hrs.filter(horizon=model_horizon_value)

            num_horizon_signals_24_hrs = horizon_signals_24_hrs.count()
            stats[signal_name][horizon_string]["num_signals_24_hrs"] = num_horizon_signals_24_hrs

            num_horizon_signals_prev_24_hrs = horizon_signals_prev_24_hrs.count()
            # stats["signals"][horizon_string]["num_signals_prev_24_hrs"] = num_horizon_signals_prev_24_hrs

            num_horizon_signals_24_hrs_delta = num_horizon_signals_24_hrs - num_horizon_signals_prev_24_hrs

            if num_horizon_signals_prev_24_hrs > 0:
                num_horizon_signals_24_hrs_delta_percent = \
                    float(num_horizon_signals_24_hrs_delta) / num_horizon_signals_prev_24_hrs
            else:
                num_horizon_signals_24_hrs_delta_percent = 0.0
                stats[signal_name][horizon_string]["num_signals_24_hrs_delta_percent"] = \
                    num_horizon_signals_24_hrs_delta_percent

    return stats
