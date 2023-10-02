import simplejson as json
import decimal
import pprint

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Max, Min
from django.views.decorators.cache import never_cache

from daa.atlas.models import Change, Gene, Tissue, Reference, Organism, Relationship, Percentage, Equation, Dataset
from daa.atlas.view_functions import generate_species_options, show_sidebar

class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)

@never_cache
def graph(request):
    """ Take a list of saved changes and make a graph out of it """ 

    data = {} 
    datapoints = []
    labels = []
    setup = []

    saved = request.session.get('saved')
    if saved is not None:
        nothing_saved = False
        
        month_values = Change.objects.filter(time_measure='months').aggregate(minage=Min('starts_age'), maxage=Max('ends_age'))
        year_values = Change.objects.filter(time_measure='years').aggregate(minage=Min('starts_age'), maxage=Max('ends_age'))
        setup = {'months': [month_values['minage']-1, month_values['maxage']+5], 'years': [year_values['minage']-20, year_values['maxage']+20]}

        changes = Change.objects.filter(identifier__in=saved.keys())

        # Make a list of dataset labels
        dsl = {} #set()
        for cds in changes:
            try:
                d = cds.data.dataset
                ds = d.datapoint_set.all()
                tmpset = set()
                if cds.process_measured.name not in dsl:
                    dsl[cds.process_measured.name] = set()
                for p in ds:
                    tmpset.add(p.label)
                dsl[cds.process_measured.name].update(tmpset)
            except:
                pass

        for c in changes:
            print c
            try:
                eq = c.data.equation
                y1 = (eq.coefficiant * c.starts_age) + eq.intercept 
                y2 = (eq.coefficiant * c.ends_age) + eq.intercept

                max_age = setup[c.time_measure][1]

                y3 = (eq.coefficiant * max_age) + eq.intercept

                if c.data.plot not in data:
                    data[c.data.plot] = {}
                if c.time_measure not in data[c.data.plot]:
                    data[c.data.plot][c.time_measure] = {}
                if 'Relative Value' not in data[c.data.plot][c.time_measure]:
                    data[c.data.plot][c.time_measure]['Relative Value'] = []

                data[c.data.plot][c.time_measure]['Relative Value'].append({'name': c.name, 'process_measured': c.process_measured.name, 'points': [[c.starts_age, y1], [c.ends_age, y2]], 'extrapolation': [[c.ends_age, y2], [max_age, y3]], 'percentage_change': eq.percentage_change, 'url': reverse('daa.atlas.views.change', args=[c.identifier]), 'time_measure': c.time_measure, 'type': c.type.title()})
            except Equation.DoesNotExist:
                try:
                    print 'hello'
                    pc = c.data.percentage
                    y1 = 1
                    y2 = 1 - (c.data.percentage_change/100)*-1 if c.data.percentage_change < 1 else 1 + (c.data.percentage_change/100)*1

                    max_age = c.ends_age #setup[c.time_measure][1]

                    y3 = 1 - (c.data.percentage_change/100)*-1 if c.data.percentage_change < 1 else 1 + (c.data.percentage_change/100)*1

                    #plot_as = c.data.plot if c.data.plot is not None else 'linear'
                    plot_as = c.data.plot if (c.data.plot is not None and c.data.plot != 'none') else 'linear'

                    if plot_as not in data:
                        data[plot_as] = {}
                    if c.time_measure not in data[plot_as]:
                        data[plot_as][c.time_measure] = {}
                    if 'Relative Value' not in data[plot_as][c.time_measure]:
                        data[plot_as][c.time_measure]['Relative Value'] = []
                    
                    data[plot_as][c.time_measure]['Relative Value'].append({'name': c.name, 'process_measured': c.process_measured.name, 'points': [[c.starts_age, y1], [c.ends_age, y2]], 'extrapolation': [[c.ends_age, y2], [max_age, y3]], 'percentage_change': pc.percentage_change, 'url': reverse('daa.atlas.views.change', args=[c.identifier]), 'time_measure': c.time_measure, 'type': c.type.title()})

                except Percentage.DoesNotExist:
                    try:
                        d = c.data.dataset
                        ds = d.datapoint_set.all()
                        cdsl  = dsl[c.process_measured.name]
                        cdsl = list(cdsl)
                        cdsl.sort()
                        points = map(lambda x: 0, cdsl)
                        for p in ds:
                            points[cdsl.index(p.label)] = p.point
                        if c.data.plot not in data:
                            data[c.data.plot] = {}
                        if c.time_measure not in data[c.data.plot]:
                            data[c.data.plot][c.time_measure] = {}
                        if c.process_measured.name.title() not in data[c.data.plot][c.time_measure]:
                            data[c.data.plot][c.time_measure][c.process_measured.name.title()] = []
                        data[c.data.plot][c.time_measure][c.process_measured.name.title()].append({'name': c.name, 'process_measured': c.process_measured.name, 'points': points, 'labels': cdsl, 'measure': c.data.measure, 'url': reverse('daa.atlas.views.change', args=[c.identifier])})
                    except Dataset.DoesNotExist:
                        pass
    else:
        nothing_saved = True


    pprint.pprint(data)

    return render_to_response('graph.html', {
            'title': 'Graph saved changes',
            'meta_description': 'The Digital Ageing Atlas is a portal that contains molecular, pathological, physiological and psychological changes that are relevant to the process of ageing, either directly or indirectly.',
            'nothing_saved': nothing_saved,
            'species_options': generate_species_options(request),
            'use_sidebar': show_sidebar(request),
            'data': json.dumps(data, use_decimal=True),
            'labels': json.dumps(labels),
            'setup': json.dumps(setup),
        }, context_instance=RequestContext(request))
