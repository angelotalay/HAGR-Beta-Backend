import csv
import re

from django.core.management.base import BaseCommand, CommandError

from daa.genage_model.models import Model 
from daa.fetchscript.fetch import FetchDetails

class Command(BaseCommand):
    help = 'Iterate through all entries and update information to current'
    args = '<from>'

    def handle(self, *args, **options):
        f = args[0] if len(args) > 0 else 0
        all_entries = Model.objects.all()[f:]

        f = FetchDetails()

        for i, entry in enumerate(all_entries):
            try:
                details = f.fetchDetailsFromEntrez(entry.entrez_id)
                entry.symbol = details['symbol']
                entry.alias = details['alias']
                if entry.name == '' or entry.name is None:
                    entry.name = details['name']
                entry.save()
            except:
                pass

            print i, entry
