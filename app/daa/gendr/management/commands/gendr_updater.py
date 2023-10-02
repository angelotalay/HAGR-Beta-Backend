import csv
import re

from django.core.management.base import BaseCommand, CommandError

from daa.gendr.models import Gene, Expression
from daa.fetchscript.fetch import FetchDetails

class Command(BaseCommand):
    help = 'Iterate through all entries and update information to current'

    def handle(self, *args, **options):
        gene_entries = Gene.objects.all()
        exp_entries = Expression.objects.all()

        f = FetchDetails()

        for entry in gene_entries:
            details = f.fetchDetailsFromEntrez(entry.entrez_id)
            entry.symbol = details['symbol']
            entry.alias = details['alias']
            entry.save()

            print entry

        for entry in exp_entries:
            details = f.fetchDetailsFromEntrez(entry.entrez_id)
            entry.symbol = details['symbol']
            entry.alias = details['alias']
            entry.ensembl = details['ensembl']
            entry.save()

            print entry
