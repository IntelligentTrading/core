from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Try if Talib works"

    def handle(self, *args, **options):
        import numpy
        import talib

        close = numpy.random.random(100)
        output = talib.SMA(close)
        print(output)
