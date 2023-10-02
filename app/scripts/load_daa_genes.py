import sys
import os
import csv

sys.path.append('/srv/www/beta.ageing-map.org/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'daa.settings'

from daa.atlas.models import *
from daa.fetchscript.fetch import FetchDetails, FetchReference

with open('../daa/atlas/data/daa_v8.txt','rb') as f:

    reader = csv.DictReader(f, delimiter='\t')
    count = 0
    for record in reader:
        count += 1
        print(count)
        try:
            gene = Gene.objects.get(entrez_id=record['entrez_id'])
        except:
            f = FetchDetails()
            results = f.fetchDetailsFromEntrez(record['entrez_id'])
            if record['organism'] == 'rat':
                record['organism'] = 'Rat'
            if record['organism'] == 'mouse':
                record['organism'] = 'Mouse'
            if record['organism'] == 'human':
                record['organism'] = 'Human'
            print(record['organism'])
            organism = Organism.objects.get(common_name=record['organism'])
            gene = Gene(organism=organism, entrez_id = record['entrez_id'], name = results['name'], symbol = results['symbol'], alias = results['alias'], description = results['description'], omim = results['omim'], ensembl = results['ensembl'], unigene = results['unigene'])
            gene.save()
