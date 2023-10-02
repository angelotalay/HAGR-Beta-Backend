import csv
import sys
import os

sys.path.append('/srv/www/beta.ageing-map.org/')
#sys.path.append('/Users/work/Projects/DAA/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'daa.settings'

from daa.longevity.models import Variant, Gene, VariantGroup, Population
from daa.django_libage.models import BibliographicEntry, Citation, Tag, Source
from daa.fetchscript.fetch import FetchDetails, FetchReference

def checkOrGetGene(entrez_id):
    try:
        gene = Gene.objects.get(entrez_id=entrez_id)
    except:
        gd = fd.fetchDetailsFromEntrez(entrez_id)
        up = fd.translateID(entrez_id, 'P_ENTREZGENEID', 'ID')
        gene = Gene(entrez_id=entrez_id, name=gd['name'], symbol=gd['symbol'], alias=gd['alias'], description=gd['description'], omim=gd['omim'], ensembl=gd['ensembl'], unigene=gd['unigene'], cytogenetic_location=gd['chromosome_location'], uniprot=up)
        gene.save()
    return gene

filename = sys.argv[1]

with open(filename) as ld: #'../HAGR/DataSources/Longevity-Associated Gene Studies Classified Corrected_Mapped.csv') as ld:
    for rid, r in enumerate(csv.DictReader(ld)):
        
        #print r
        print rid
        
        hasSNPIdentifiers = False
        genesAreIdentifiers = False
        identifiers = []
        group = None

        gene_list = r['gene symbol'].split(',')
        gene = []
        entrez_id = []
        fd = FetchDetails()
        
        if 'variants' in r:
            identifiers = r['variants'].split(',')
            if identifiers[0].strip().startswith('rs'):
                hasSNPIdentifiers = True
        else:
            identifiers.append(None)

        if not hasSNPIdentifiers:
            if 'entrez id' not in r:
                for g in gene_list:
                    if g != '':
                        eid = fd.convertToEntrezGeneID(g)
                        if eid != '' and eid is not None:
                            entrez_id.append(eid)
            else:
                if r['entrez id'] != '':
                    entrez_id = [r['entrez id']]

            if len(entrez_id) > 0:
                gene = [checkOrGetGene(e) for e in entrez_id]

        population, c = Population.objects.get_or_create(name=r['population'])

        ref = BibliographicEntry.objects.get_or_create_from_pubmed(r['pubmed'])

        variantsToGroup = []

        if len(gene) > 1 and len(identifiers) <= 1:
            identifiers = gene[:]
            genesAreIdentifiers = True

        if len(identifiers) > 1:
            group = VariantGroup(association=r['association'])
            group.save()

        genes = []
        for n,i in enumerate(identifiers):
            if hasSNPIdentifiers:
                snpDetails = fd.fetchDetailsFromdbSNP(i) 
                if snpDetails['entrez_id'] is not None and snpDetails['entrez_id'] != '':
                    gene[:] = []
                    gene.append(checkOrGetGene(snpDetails['entrez_id']))
                    genes.append(gene)
                elif snpDetails['entrez_id'] is None and i.startswith('rs'):
                    gene[:] = []
                else:
                    gene[:] = []
                    if n < len(gene_list):
                        lookup = gene_list[n]
                    elif len(gene_list) > 0:
                        lookup = gene_list[0]
                    else:
                        lookup = None
                    eid = fd.convertToEntrezGeneID(lookup)
                    if eid != '':
                        gene.append(checkOrGetGene(eid))
                    else:
                        print lookup

            if 'location' not in r or r['location'] == '':
                if len(gene) > 0:
                    if n < len(gene):
                        loc = gene[n].cytogenetic_location
                    else:
                        loc = gene[0].cytogenetic_location
                else:
                    loc = r['location']
            else:
                loc = r['location']

            if i is None or genesAreIdentifiers:
                identifier = None
            else:
                identifier = i.strip()

            if len(gene) > 1:
                g = gene[n]
            elif len(gene) == 1:
                g = gene[0]
            else:
                g = None

            #print identifier 
            #print loc
            #print g

            variant = Variant(location=loc, study_design=r['study design'], conclusions=r['conclusions'], association=r['association'], gene=g, population=population, quickref=ref.get_short_reference(), quickpubmed=ref.pubmed, quickyear=ref.year, identifier=identifier) 
            variant.save()

            print 'L:', rid, n
            print 'Lv: ', variant.id, n

            if len(identifiers) > 1:
                variant.variantgroup = group
                variant.save()

        if len(identifiers) > 1:
            ltype = u'group'
            db_identifier = u'G'+str(group.id)
            if len(genes) > 1:
                location = u'in {} genes'.format(len(genes))
            elif len(gene) > 0:
                location = gene[0].symbol
            else:
                location = loc
        else:
            db_identifier = str(variant.id)
            ltype = u'variant'
            if len(gene) > 0:
                location = gene[0].symbol
            else:
                location = loc

        title = u'{association} longevity {type} {location} for tested {population} population'.format(association=unicode(r['association']), type=unicode(ltype), location=unicode(location), population=unicode(population.name))
        source = Source.objects.get(short_name='longevity')
        cited = Citation(identifier=db_identifier, title=title, source=source)
        cited.save()
        ref.citations.add(cited)
