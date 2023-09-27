import csv

from django.core.management.base import BaseCommand, CommandError

from daa.genage_human.models import Name 

class Command(BaseCommand):
    args = '<file>'
    help = 'Populate the ensembl field with correct data'

    def handle(self, *args, **options):
        all_entries = Name.objects.all()
        ensembl_ids = {}

        with open(args[0]) as ensembl_file:
            for row in csv.DictReader(ensembl_file, delimiter="\t"):
                ensembl_ids[row['EntrezGene ID']] = row['Ensembl Gene ID']        

        for entry in all_entries:
            if str(entry.entrez_id) in ensembl_ids:
                for l in entry.links_set.all():
                    l.ensembl = ensembl_ids[str(entry.entrez_id)]
                    l.save()
