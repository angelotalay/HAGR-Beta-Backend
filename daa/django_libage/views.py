import json
import math
import urllib2
import urllib

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.html import strip_tags

# For native querying of the database one class needs to be imported
from daa.atlas.models import Change
from daa.atlas.tables import ChangeTable

def reference(request, identifier):
    from daa.atlas.view_functions import generate_species_options, show_sidebar
    url = '{0}/details/{1}/{2}/'.format(settings.LIBAGE_ENDPOINT, settings.LIBAGE_DATABASE, identifier)
    try:
        response = urllib2.urlopen(url).read()
    except urllib2.URLError, urllib2.HTTPError:
        response = '{}'
    results = json.loads(response)

    changes = Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(identifier__in=results['citations'])

    if request.GET.get('export') == 'True':
        export_header = ['Identifier','Change name','Change type', 'Change gender', 'Age change starts', 'Age change ends', 'Description', 'Tissues', 'Gene', 'Properties', 'Type of data', 'Process measured', 'Sample size', 'Method of collection', 'Data transforms', 'Percentage change', 'P value', 'Coefficiant', 'Intercept', 'Species']
        export_data = ""
        for e in changes:
            tissues = u", ".join([t.name.title() for t in e.tissues.all()])
            gene = e.gene.compound_name() if e.gene is not None else u""
            properties = u", ".join([prp.name for prp in e.properties.all()])
            process_measured = e.process_measured.name if e.process_measured is not None else u''
            try:
                d = e.data
                if d is not None:
                    data = {
                        'type': d.type,
                        'sample_size': d.sample_size,
                        'method_collection': d.method_collection,
                        'data_transforms': d.data_transforms,
                        'percentage_change': d.percentage_change,
                        'p_value': d.p_value,
                    }
                    try:
                        eq = d.data.equation
                        equation = {
                            'coefficiant': eq.coefficiant,
                            'intercept': eq.intercept,
                        }
                    except:
                        equation = {}
                    data.update(equation)
                else:
                    data = {}
            except ObjectDoesNotExist:
                data = {}

            tmp = u"{id}\t{name}\t{type}\t{gender}\t{start}\t{end}\t{description}\t{tissues}\t{gene}\t{properties}\t{dtype}\t{measure}\t{dsample}\t{dmethod}\t{dtransforms}\t{dpercent}\t{dpvalue}\t{dcoefficiant}\t{dintercept}\t{species}\n".format(id=e.identifier, name=e.name, type=e.type, gender=e.gender, start=e.starts_age, end=e.ends_age, description=e.description, tissues=tissues, gene=gene, properties=properties, dtype=data.get('type', ''), measure=process_measured, dsample=data.get('sample_size', ''), dmethod=data.get('method_collection', ''), dtransforms=data.get('data_transforms', ''), dpercent=data.get('percentage_change', ''), dpvalue=data.get('p_value', ''), dcoefficiant=data.get('coefficiant', ''), dintercept=data.get('intercept', ''), species=e.organism.name)
            export_data += tmp
        resp = HttpResponse(u"\t".join(export_header)+u"\n"+export_data, content_type="text/plain")
        resp['Content-Disposition'] = 'attachment; filename={}.txt'.format(strip_tags('The Digital Ageing Atlas | '+results['reference']).replace(' ', '_'))
    else:
        table = ChangeTable(changes, order_by=request.GET.get('sort'))
        table.paginate(page=request.GET.get('page', 1))
        resp = render(request, 'entry.html', {
            'title': 'The Digital Ageing Atlas | '+results['reference'],
            'ref': results['reference'], 
            'species_options': generate_species_options(request),
            'table': table,
            'libage_url': settings.LIBAGE_URL,
            'use_sidebar': True, #show_sidebar(request),
        })
    
    return resp 

def _search_count(term):
    """
    Used internally to get number of results for given term
    """
    url = '{0}/count/{1}/?q={2}'.format(settings.LIBAGE_ENDPOINT, settings.LIBAGE_DATABASE, urllib.quote(term))
    try:
        response = urllib2.urlopen(url).read()
    except:
        response = '{"count": 0, "results": []}'
    results = json.loads(response)
    return results

def search_references(request):
    q = '' if request.GET.get('s') is None else request.GET.get('s')
    sort = 'author' if request.GET.get('sort') is None else request.GET.get('sort')
    page = 1 if request.GET.get('page') is None else int(request.GET.get('page'))
    per_page = 20

    start = page-1 if page == 1 else page*per_page-1
    end = page*per_page if page == 1 else page*per_page+per_page

    url = '{0}/search/{1}/{2}/{3}/?q={4}&sort={5}'.format(settings.LIBAGE_ENDPOINT, settings.LIBAGE_DATABASE, start, end, urllib.quote(q), sort)
    try:
        response = urllib2.urlopen(url).read()
    except:
        response = '{"count": 0, "results": []}'
    results = json.loads(response)

    num_pages = int(math.ceil(results['count']/per_page))
    page_range = range(page-2 if page-2 > 0 else 1, page+3 if page+3 < num_pages else num_pages)  

    if q != '':
        title = 'Bibliography search: {0} ({1} entries)'.format(q,results['count'])
    else:
        title = 'Bibliography'
    
    return render(request, 'references.html', {
        'title': title,
        'results': results['results'],
        'count': results['count'],
        'query': q,
        'libage_url': settings.LIBAGE_URL,
        'sort': sort,
        'num_pages': num_pages,
        'page': page,
        'page_range': page_range,
        'previous': page-1 if page-1 > 1 else 1,
        'next': page+1 if page+1 < num_pages else num_pages,
    })
