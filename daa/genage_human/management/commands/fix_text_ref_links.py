import csv
import re

from django.core.management.base import BaseCommand, CommandError

from daa.genage_human.models import Name 
from daa.django_libage.models import Citation, BibliographicEntry

class Command(BaseCommand):
    args = '<file>'
    help = 'Populate the ensembl field with correct data'

    ref_to_ref = {}

    def fixref(self, m):
        if m.group(1) in self.ref_to_ref:
            return u'[{}]'.format(self.ref_to_ref[m.group(1)])
        else:
            return m.group()

    def handle(self, *args, **options):
        all_entries = Name.objects.all()

        with open(args[0]) as map_file:
            for row in csv.reader(map_file, delimiter=","):
                if row[1] != '':
                    try:
                        r = BibliographicEntry.objects.get(pubmed=row[1])
                        self.ref_to_ref[row[0]] = r.id
                    except:
                        print row[1]

        for entry in all_entries:
            fs = entry.features_set.all()[0]
            desc = fs.phenotype #entry.features_set.all()[0].phenotype
            desc = re.sub(r'\[(\d+)\]', self.fixref, desc)
            fs.phenotype = desc
            fs.save()
            print entry
