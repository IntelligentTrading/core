"""
 Prints CSV of all fields of a model.
"""
import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps



class Command(BaseCommand):
    help = ("Output the specified model as CSV")
    args = 'Mode Name (Price or Volume)'

    def add_arguments(self, parser):
        "modelname: Price or Volume"
        parser.add_argument('modelname', type=str)

    def handle(self, *app_labels, **options):
        modelname = options['modelname']
        model = apps.get_model('indicator', modelname)
        print(f"exporting model:{model}")
        field_names = [f.name for f in model._meta.fields]
        print(f"field names: {field_names}")

        with open(f'{modelname}.csv', 'ab') as csvfile:
            csvfile.write(f"{field_names}")
            for instance in model.objects.all()[:10]:
                csvfile.write([getattr(instance, f) for f in field_names])

        # writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
        # writer.writerow(field_names)
        # for instance in model.objects.all()[:10]:
        #     writer.writerow([getattr(instance, f) for f in field_names])
