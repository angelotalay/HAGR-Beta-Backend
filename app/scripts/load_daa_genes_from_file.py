import sys
import os
import csv

sys.path.append('/srv/www/beta.ageing-map.org/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'daa.settings'

from daa.atlas.models import *
from daa.fetchscript.fetch import FetchDetails, FetchReference

with open('/tmp/atlas_genes.tsv','rb') as f:

    reader = csv.DictReader(f, delimiter='\t')

    for record in reader:
        try:
            gene = Gene.objects.get(entrez_id=record['entrez_id'])
            print ("record entrez_id: " + record['entrez_id'])
        except:
            print ("record not found, entrez_id: '" + record['entrez_id'] + "'")
            organism = Organism.objects.get(id=record['organism_id'])
            print(organism)
            gene = Gene(organism=organism, entrez_id = record['entrez_id'], name = record['name'], symbol = record['symbol'], alias = record['alias'], description = record['description'], omim = record['omim'], ensembl = record['ensembl'], unigene = record['unigene'], in_genage = record['in_genage'])
            gene.save()            
