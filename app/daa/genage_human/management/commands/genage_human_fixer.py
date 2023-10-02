import csv
import re

from django.core.management.base import BaseCommand, CommandError

from daa.genage_human.models import Name, Go 
from daa.fetchscript.fetch import FetchDetails

class Command(BaseCommand):
    args = '<start_id>'
    help = 'Iterate through all entries and update information to current'

    def handle(self, *args, **options):
        all_entries = Name.objects.filter(id_hagr__gt=args[0])

        f = FetchDetails()

        for entry in all_entries:
            uniprot = f.translateID(entry.entrez_id, 'P_ENTREZGENEID', 'ID')
            details = f.fetchDetailsFromUniProt(uniprot)

            links = entry.links_set.all()[0] 
            links.swissprot = details['uniprot']
            links.save()

            print entry.id_hagr, entry
