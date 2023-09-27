import csv
import re

from django.core.management.base import BaseCommand, CommandError

from daa.genage_human.models import Name, Go 
from daa.fetchscript.fetch import FetchDetails

class Command(BaseCommand):
    help = 'Iterate through all entries and update information to current'

    def handle(self, *args, **options):

        update_go = False

        all_entries = Name.objects.all()

        f = FetchDetails()

        for entry in all_entries:
            details = f.fetchDetailsFromEntrez(entry.entrez_id)
            entry.symbol = details['symbol']
            entry.aliases = details['alias']
            entry.save()

            features = entry.features_set.all()[0]
            features.band = details['chromosome_location']
            features.location_start = int(details['location_start'])
            features.location_start = int(details['location_end'])
            features.save()

            if update_go:
                for go in details['go']:
                    term = Go(hagrid=entry, go=go['go'], name=go['name'], type=go['type'][0])
                    term.save()

            print entry
