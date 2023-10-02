import operator
import json
import re

from django.utils.safestring import mark_safe
from django.db.models import Q
from django.db.models import Count

from daa.atlas.models import Change, Gene, Tissue, Reference, Organism
from daa.atlas.queries import change_query, tissue_query, gene_query, reference_query

from daa.django_libage.views import _search_count

def generate_species_options(request):
    selected = request.GET.getlist('species[]')
    species = Organism.objects.filter(hasDatabase=True).order_by('common_name')
    html = ''
    for s in species:
        if (len(selected) < 1 and s.taxonomy_id == 9606) or str(s.taxonomy_id) in selected:
            checked = 'checked="checked"'
        else:
            checked = ''
        html += '<label><input type="checkbox" name="species[]" value="{0}" {1} /> {2}</label>'.format(str(s.taxonomy_id), checked, s.common_name)
    return mark_safe(html)

def show_sidebar(request, override_use=None):
    if override_use == True:
        return True
    elif override_use == False:
        return False

    if request.session.get('saved') != None:
        return True
    else:
        return False

def generate_filter_field_list(fltr, request):
    fields = {}
    if fltr is not None:
        for fld in fltr.form:
            classpath = str(fld.field).split('.')
            objname = classpath[len(classpath)-1].split(' ')[0]
            fields[fld.name] = {'type': objname, 'html': fld.as_widget()}
        for actv in request.GET:
            lookup = False
            if actv.startswith('lookups'):
                lookup_key = actv
                actv = re.search('lookups\[(.*?)\]', actv).group(1)
                lookup = True
            if actv in fields:
                if lookup is True:
                    fields[actv]['lookup_type'] = request.GET.get(lookup_key)
                else:
                    fields[actv]['active'] = True
    else:
        fields = {}
    return fields   

def generate_simple_chart_object(request, name, data):
    categories = []
    points = []
    for d in data.dataset.datapoint_set.all():
        categories.append(d.label)
        points.append(d.point)
    options = {
        'chart': {
            'renderTo': 'chart',
            'type': data.plot,
        },
        'title': {
            'text': name,
        },
        'xAxis': {
            'categories': categories,
            'title': {
                'text': 'Age'
            }
        },
        'yAxis': {
            'title': {
                'text': data.process_measured
            }
        },
        'series': [
            { 
                'name': name,
                'data': points,
            }
        ],
    }
    return json.dumps(options)

def get_stats(s, species=[]):
    if s is None:
        s = ''
    if len(species) < 1:
        for all_species in Organism.objects.filter(hasDatabase=True):
            species.append(Q(organism__taxonomy_id=all_species.taxonomy_id))

    physiological = Change.objects.filter(type='physiological').filter(reduce(operator.or_, species), change_query(s), hide=False).aggregate(count=Count('identifier'))
    pathological = Change.objects.filter(type='pathological').filter(reduce(operator.or_, species), change_query(s), hide=False).aggregate(count=Count('identifier'))
    molecular = Change.objects.filter(type='molecular').filter(reduce(operator.or_, species), change_query(s), hide=False).aggregate(count=Count('identifier'))
    psychological = Change.objects.filter(type='psychological').filter(reduce(operator.or_, species), change_query(s), hide=False).aggregate(count=Count('identifier'))

    gene = Gene.objects.filter(reduce(operator.or_, species), gene_query(s)).aggregate(count=Count('entrez_id'))
    tissue = Tissue.objects.filter(tissue_query(s)).aggregate(count=Count('evid'))
    #reference =  Reference.objects.filter(reference_query(s)).aggregate(count=Count('id'))
    # Hook into LibAge app to deliver reference count
    reference = _search_count(s)

    stats = {
        'changes': {
        },
        'sections': {
        }
    }

    if physiological['count'] > 0:
        stats['changes']['physiological'] = physiological 
    if pathological['count'] > 0:
        stats['changes']['pathological'] = pathological
    if molecular['count'] > 0:
        stats['changes']['molecular'] = molecular
    if psychological['count'] > 0:
        stats['changes']['psychological'] = psychological

    if gene['count'] > 0:
        stats['sections']['gene'] = gene
    if tissue['count'] > 0:
        stats['sections']['tissue'] = tissue
    if reference['count'] > 0:
        stats['sections']['reference'] = reference

    return stats
