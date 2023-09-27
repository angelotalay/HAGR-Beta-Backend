import sys
import os
import csv

sys.path.append('/srv/www/beta.ageing-map.org/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'daa.settings'

from daa.atlas.models import *
from daa.fetchscript.fetch import FetchDetails, FetchReference
from django.core.exceptions import ObjectDoesNotExist
from daa.django_libage.models import BibliographicEntry, Citation, Source, Tag
from django.conf import settings

VALID_CHANGE = (
        'name',
        'type',
        'starts_age',
        'ends_age',
        'type',
        'gender',
        'description',
        'time_measure',
)

VALID_DATA = (
        'process_measured',
        'is_negative',
        'sample_size',
        'measure',
        'method_collection',
        'data_transforms',
        'p_value',
)

REQUIRED_PERCENTAGE = (
        'type',
        'process_measured',
        'percentage_change',
)

REQUIRED_EQUATION = (
        'type',
        'plot',
        'coefficiant',
        'intercept',
        'percentage_change',
        'process_measured',
)

REQUIRED = (
        'name',
        'type',
        'starts_age',
        'ends_age',
        'organism',
        'tissues',
        'pubmed',
)

VALID = (
        'gender',
        'description',
        'time_measure',
        'entrez_id',
        'properties',
)

VALID_HEADERS = REQUIRED + VALID + VALID_DATA + REQUIRED_PERCENTAGE + REQUIRED_EQUATION

with open('../daa/atlas/data/daa_v8_259876_145239_76177_90597_455199.txt','rb') as f:
    reader = csv.DictReader(f, delimiter='\t')

    count = 0
    for record in reader:
        count += 1
        print(count)
        if record['organism'] == 'rat':
            record['organism'] = 'Rat'
        if record['organism'] == 'mouse':
            record['organism'] = 'Mouse'
        if record['organism'] == 'human':
            record['organism'] = 'Human'
        try:
            gene = Gene.objects.get(entrez_id=record['entrez_id'])
        except:
            print(record['organism'])
            f = FetchDetails()
            results = f.fetchDetailsFromEntrez(record['entrez_id'])
            organism = Organism.objects.get(common_name=record['organism'])
            gene = Gene(organism=organism, entrez_id = record['entrez_id'], name = results['name'], symbol = results['symbol'], alias = results['alias'], description = results['description'], omim = results['omim'], ensembl = results['ensembl'], unigene = results['unigene'])
            gene.save()

        if record['coefficiant'] != '':
            eq = {k:v for k,v in record.iteritems() if k in (REQUIRED_EQUATION + VALID_DATA) and k not in ('type', 'process_measured',)}
            data = Equation(**eq)
            data.save()
        elif record['percentage_change'] != '':
            eq = {k:v for k,v in record.iteritems() if k in REQUIRED_PERCENTAGE + VALID_DATA and k not in ('type', 'process_measured',)}
            data = Percentage(**eq)
            data.save()
        try:
            process_measured = ProcessMeasured.objects.get(name=record['process_measured'])
        except KeyError:
            process_measured = None

        try:
            organism = Organism.objects.get(common_name=record['organism'])
        except KeyError:
            organism = Organism.objects.get(common_name='Human')

        ch = {k:v for k,v in record.iteritems() if k in VALID_CHANGE}
        c = Change(gene=gene, organism=organism, data=data, process_measured=process_measured, **ch)
        c.save()

        for t in record['tissues'].split(','):
           if t.strip() == 'eye':
               t = 'visual apparatus'
           elif t.strip() == 'gonads':
               if record['gender'] == 'male':
                   t = 'testis';
               else:
                   t = 'ovary'
           elif t.strip() == 'cd14':
               t = 'monocyte'
           elif t.strip() == 'cd4':
               t = 'T cell'
           elif t.strip() == 'tail':
               t = 'tail skin'
           elif t.strip() == 'myoblast':
               t = 'myoblast progenitor'
           elif t.strip() == 'sabmandibular gland':
               t = 'submandibular gland'
           elif t.strip() == 'haematopoietic stem cells':
               t = 'hematopoietic stem cells'
           elif t.strip() == 'cd 4':
               t = 'T cell'
           else: 
               pass
           c.tissues.add(Tissue.objects.get(name=t))

        if record['pubmed'] != '' and record['pubmed'] != 'NA':
            try:
                b = BibliographicEntry.objects.get(pubmed=record['pubmed'])
            except ObjectDoesNotExist:
                fref = FetchReference()
                results = fref.fetchPubmed(record['pubmed'])
                del results['author_initials']
                del results['authors']
                b = BibliographicEntry(**results)
                b.save()
                b = BibliographicEntry.objects.get(pubmed=record['pubmed'])

            source = Source.objects.get(short_name=settings.LIBAGE_DATABASE)
            citation,c = Citation.objects.get_or_create(identifier=c.identifier, title=c.name, source=source)
            b.citations.add(citation)
