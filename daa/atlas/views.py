import operator
import json
import urlparse

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.db.models import Q
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.core import serializers
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponse, Http404
from django.core import serializers
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control, patch_cache_control
from django.utils.html import strip_tags

from daa.atlas.cache_control import expire_view_cache

from daa.atlas.models import Change, Gene, Tissue, Reference, Organism, Relationship
from daa.atlas.tables import ChangeTable, MolecularTable, PathologicalTable, PhysiologicalTable, PsychologicalTable, GeneTable, TissueTable, ReferenceTable
from daa.atlas.view_functions import generate_species_options, get_stats, generate_simple_chart_object, generate_filter_field_list, show_sidebar
from daa.atlas.queries import change_query, tissue_query, gene_query, reference_query
from daa.atlas.filters import TissueFilterSet, ChangeFilterSet, GeneFilterSet, ReferenceFilterSet

from daa.go_db.models import Association, Term, GeneProduct

from daa.ortholog.models import Ortholog

def index(request):
    """ Render the default index page """
    stats = [] 
    for species in Organism.objects.filter(hasDatabase=True):
        stats.append([{'name': species.common_name, 'id': species.taxonomy_id}, get_stats('', species=[Q(organism__taxonomy_id=species.taxonomy_id)])])
    stats = sorted(stats, key=lambda x: x[0])
    latest = ''
    resp = render_to_response('index.html', {
            'title': 'Welcome to the Digital Ageing Atlas, the portal of ageing related changes',
            'meta_description': 'The Digital Ageing Atlas is a portal that contains molecular, pathological, physiological and psychological changes that are relevant to the process of ageing, either directly or indirectly.',
            'stats': stats,
            'latest': latest,
            'species_options': generate_species_options(request),
            'use_sidebar': show_sidebar(request),
        }, context_instance=RequestContext(request))
    if show_sidebar(request):
        patch_cache_control(resp, no_cache=True, must_revalidate=True, max_age=0)
    return resp

def about(request):
    return render_to_response('about.html', {
        'title': 'About the Digital Ageing Atlas',
        'meta_description': 'The Digital Ageing Atlas is a portal that contains molecular, pathological, physiological and psychological changes that are relevant to the process of ageing, either directly or indirectly.',
        'species_options': generate_species_options(request),
    }, context_instance=RequestContext(request))

def help(request):
    return render_to_response('help.html', {
        'title': 'Help and Support',
        'meta_description': 'The Digital Ageing Atlas is a portal that contains molecular, pathological, physiological and psychological changes that are relevant to the process of ageing, either directly or indirectly.',
        'species_options': generate_species_options(request),
    }, context_instance=RequestContext(request))

def downloads(request):
    return render_to_response('downloads.html', {
        'title': 'Downloads',
        'meta_description': 'The Digital Ageing Atlas is a portal that contains molecular, pathological, physiological and psychological changes that are relevant to the process of ageing, either directly or indirectly.',
        'species_options': generate_species_options(request),
    }, context_instance=RequestContext(request))

def contact(request):
    if 'submit' in request.POST:
        send_mail('Contact from {0} via the Digital Ageing Atlas'.format(request.POST.get('name')), request.POST.get('comments'), request.POST.get('email'), ['thomas.craig@theramblingchronicles.co.uk'], fail_silently=False)
    return render_to_response('contact.html', {
        'title': 'Contact or Contribute',
        'meta_description': 'The Digital Ageing Atlas is a portal that contains molecular, pathological, physiological and psychological changes that are relevant to the process of ageing, either directly or indirectly.',
        'species_options': generate_species_options(request),
    }, context_instance=RequestContext(request))

def results(request):
    """ Render the results page based on query list terms """
    s = request.GET.get('s')
    species = request.GET.getlist('species[]')
    showtype = request.GET.get('t')
    limit_to = request.GET.get('l')
    limit_id = request.GET.get('lid')

    if s == None:
        s = ''
    else:
        s = s.strip()

    species_list = []
    if len(species) > 0:
        for sp in species:
            species_list.append(Q(organism__taxonomy_id=sp))
    else:
        for sp in Organism.objects.all():
            species_list.append(Q(organism__taxonomy_id=sp.taxonomy_id))

    use_sidebar = True
    is_pre_result = False
    
    if limit_to != None and limit_id != None:
        if limit_to == 'gene':
            changes = Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(reduce(operator.or_, species_list), gene__entrez_id=limit_id, hide=False)
            limit_name = Gene.objects.get(entrez_id=limit_id).symbol
        elif limit_to == 'reference':
            # Hook into LibAge app to get and deliver the results
            url = reverse('libage:search')
            return redirect(url+'?s={0}'.format(s))
        elif limit_to == 'tissue':
            selected_tissue = Tissue.objects.get(evid=limit_id)
            descendants = selected_tissue.get_descendants(include_self=True)
            limit_name = selected_tissue.name
            changes = Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(reduce(operator.or_, species_list), tissues__in=descendants)#.distinct()
        else:
            raise Http404
    else:
        changes = Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(reduce(operator.or_, species_list), change_query(s), hide=False)

    template = 'results.html'
    fields = None
    fltr = None
    stats = None

    if showtype == 'molecular':
        fltr = ChangeFilterSet(request.GET, queryset=changes.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(type='molecular', hide=False))
        table = MolecularTable(fltr.qs, order_by=request.GET.get('sort'))
    elif showtype == 'pathological':
        fltr = ChangeFilterSet(request.GET, queryset=changes.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured').prefetch_related('tissues', 'properties').filter(type='pathological', hide=False))
        table = PathologicalTable(fltr.qs, order_by=request.GET.get('sort'))
    elif showtype == 'physiological':
        fltr = ChangeFilterSet(request.GET, queryset=changes.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured').prefetch_related('properties', 'tissues').filter(type='physiological', hide=False))
        table = PhysiologicalTable(fltr.qs, order_by=request.GET.get('sort'))
    elif showtype == 'psychological':
        fltr = ChangeFilterSet(request.GET, queryset=changes.prefetch_related('properties', 'tissues', 'organism').filter(type='psychological', hide=False))
        table = PsychologicalTable(fltr.qs, order_by=request.GET.get('sort'))
    elif showtype == 'gene':
        genes = Gene.objects.select_related('organism').filter(reduce(operator.or_, species_list), gene_query(s)).annotate(number_of_changes=Count('change'))
        fltr = GeneFilterSet(request.GET, queryset=genes)
        table = GeneTable(fltr.qs, order_by=request.GET.get('sort'))
    elif showtype == 'tissue':
        tissues = Tissue.objects.filter(tissue_query(s))#.annotate(number_of_changes=Count('change'))
        rc = Tissue.objects.add_related_count(tissues, Change, 'tissues', 'number_of_changes', cumulative=True)

        fltr = TissueFilterSet(request.GET, queryset=rc)
        table = TissueTable(fltr.qs, order_by=request.GET.get('sort'))
    elif showtype == 'reference':
        '''
        references = Reference.objects.filter(reference_query(s)).annotate(number_of_changes=Count('change')).order_by('title')
        fltr = ReferenceFilterSet(request.GET, queryset=references)
        table = ReferenceTable(fltr.qs, order_by=request.GET.get('sort'))
        '''
        # Hook into LibAge app to get and deliver the results
        url = reverse('libage:search')
        return redirect(url+'?s={0}'.format(s))
    elif limit_to in ['gene', 'reference', 'tissue']:
        fltr = ChangeFilterSet(request.GET, queryset=changes)
        table = ChangeTable(fltr.qs, order_by=request.GET.get('sort'))
    else:
        template = 'pre_results.html'
        stats = get_stats(s, species_list)
        use_sidebar = None
        is_pre_result = True

    rc = ''
    if not is_pre_result:
        rc = '({0})'.format(fltr.qs.count())
    
    title = ''
    if limit_to != None:
        title = u'All changes for the {0} <span class="search-term">{1}</span>  <span class="results-count">{2}</span>'.format(limit_to, limit_name, rc)
    elif s == '' or s == None:
        title = 'All results in the Digital Ageing Atlas'
        if showtype in ['gene', 'reference', 'tissue']:
            title = u'All {0}s <span class="results-count">{1}</span>'.format(showtype, rc)
        elif showtype != '' and showtype != None:
            title = u'All {0} changes <span class="results-count">{1}</span>'.format(showtype, rc)
    else:
        title = u'Search results for <span class="search-term">{0}</span>'.format(s)
        if showtype in ['gene', 'reference', 'tissue']:
            title = u'{0}s matching your search for <span class="search-term">{1}</span> <span class="results-count">{2}</span>'.format(showtype.title(), s, rc)
        elif showtype != '' and showtype != None:
            title = u'{0} changes matching your search for <span class="search-term">{1}</span> <span class="results-count">{2}</span>'.format(showtype.title(), s, rc)

    if fltr is not None and request.GET.get('export') == 'True':
        export_header = ['Identifier','Change name','Change type', 'Change gender', 'Age change starts', 'Age change ends', 'Description', 'Tissues', 'Gene', 'Properties', 'Type of data', 'Process measured', 'Sample size', 'Method of collection', 'Data transforms', 'Percentage change', 'P value', 'Coefficiant', 'Intercept', 'Species']
        export_data = ""
        for e in fltr.qs:
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
        resp['Content-Disposition'] = 'attachment; filename={}.txt'.format(strip_tags(title).replace(' ', '_'))
    else:
        fields = generate_filter_field_list(fltr, request) 

        try:
            table.paginate(page=request.GET.get('page', 1))
        except:
            table = None

        resp = render_to_response(template, {
            'title': mark_safe(title),
            'species_options': generate_species_options(request),
            's': s,
            'table': table,
            'stats': stats,
            'type': showtype,
            'limited': True if limit_to != None else False,
            'use_sidebar': show_sidebar(request, use_sidebar),
            'keys': ('s', 't', 'species[]', 'l', 'lid', 'page', 'sort'),
            'fields': fields,
        }, context_instance=RequestContext(request))
    return resp

def anatomical(request):

    species = request.GET.get('species')
    try:
        active = Organism.objects.get(taxonomy_id=species)
    except:
        active = Organism.objects.get(taxonomy_id=9606)

    available = Organism.objects.filter(hasDatabase=True)

    title = 'Anatomical Model for {0}'.format(active.common_name)
    tissues = Tissue.objects.all().prefetch_related('change_set')
    tissues_with_count = Tissue.objects.add_related_count(tissues, Change, 'tissues', 'number_of_changes', cumulative=True)
    #all_tissues = Tissue.objects.all()
    jtissues = {}
    for t in tissues_with_count:
        jtissues[t.name] = {'type_changes_count': 0, 'evid': t.evid, 'synonyms': t.synonyms, 'number_of_changes': 0, 'url': ''}
    for t in tissues_with_count:
        dc = t.get_descendants(include_self=True)
        chngs = Change.objects.filter(tissues__in=dc, organism__common_name=active.common_name)
        tc = {}
        counted = []
        # We need to get change count per TYPE, this is the most
        # efficient way, others too time or resources consuming
        for c in chngs:
            if c.identifier not in counted:
                if c.type not in tc:
                    tc[c.type] = 0
                tc[c.type] += 1
                counted.append(c.identifier)
        type_count = [{'type__count': v, 'type': k} for k,v in tc.items()]
        jtissues[t.name] = {'type_changes_count': type_count, 'evid': t.evid, 'synonyms': t.synonyms, 'number_of_changes': chngs.count(), 'url': '{0}?l=tissue&amp;lid={1}&amp;species[]={2}'.format(reverse('daa.atlas.views.results'), str(t.evid), active.taxonomy_id), 'turl': '{0}'.format(reverse('daa.atlas.views.tissue', args=[t.evid]))}
    resp = render_to_response('anatomical.html', {
        'title': mark_safe(title),
        'species_options': generate_species_options(request),
        'use_sidebar': show_sidebar(request),
        'nodes': tissues_with_count,
        'node_lookup': jtissues,
        'species_available': available,
        'active': active,
        'jtissues': json.dumps(jtissues)
    }, context_instance=RequestContext(request))
    if show_sidebar(request):
        patch_cache_control(resp, no_cache=True, must_revalidate=True, max_age=0)
    return resp

def change(request, identifier):

    change = get_object_or_404(Change, identifier=identifier)   

    show_add_to_saved = False
    if change.starts_age > 0 and change.ends_age > 0:
        try:
            exists = change.data.equation
            show_add_to_saved = True
        except ObjectDoesNotExist:
            try:
                exists = change.data.percentage
                show_add_to_saved = True
            except ObjectDoesNotExist:
                try:
                    exists = change.data.percentage
                    show_add_to_saved = True
                except ObjectDoesNotExist:
                    pass
        except AttributeError:
            pass

    relationships = Relationship.objects.filter(change__identifier=identifier)
    rnodes = []
    rids = []
    for r in relationships:
        if r.get_root().id not in rids:
            rnodes.append(r.get_root().get_descendants(include_self=True))
            rids.append(r.get_root().id)

    resp = render_to_response('change.html', {
        'title': change.name,
        'species_options': generate_species_options(request),
        'change': change,
        'rnodes': rnodes,
        'nodes': Tissue.objects.all(),
        'use_sidebar': show_sidebar(request),
        'show_add_to_saved': show_add_to_saved,
    }, context_instance=RequestContext(request))
    if show_sidebar(request):
        patch_cache_control(resp, no_cache=True, must_revalidate=True, max_age=0)
    return resp

def gene(request, entrez_id):
    gene = get_object_or_404(Gene, entrez_id=entrez_id)
    table = ChangeTable(Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(gene__entrez_id=entrez_id), order_by=request.GET.get('sort'))
    table.paginate(page=request.GET.get('page', 1))

    unigene_split = gene.organism.name.split(' ')
    unigene = unigene_split[0][:1]+unigene_split[1][:1].lower()

    go = Association.objects.distinct('term__term_type', 'term__acc').filter(gene_product__symbol=gene.symbol, gene_product__species__ncbi_taxa_id=gene.organism.taxonomy_id).select_related('term', 'gene_product').order_by('term__term_type', 'term__acc')

    orthologs = Ortholog.objects.filter(Q(entrez_a=gene.entrez_id) | Q(entrez_b=gene.entrez_id))
    orth_ids = []
    ortholog_list = []
    for o in orthologs:
        if o.entrez_a not in orth_ids and o.entrez_a != gene.entrez_id:
            orth_ids.append(o.entrez_a)
        if o.entrez_b not in orth_ids and o.entrez_b != gene.entrez_id:
            orth_ids.append(o.entrez_b)
        if o.species_a != gene.organism.name:
            ortholog_list.append({'symbol': o.symbol_a, 'entrez_id': o.entrez_a, 'organism': o.species_a})
        else:
            ortholog_list.append({'symbol': o.symbol_b, 'entrez_id': o.entrez_b, 'organism': o.species_b})

    #ortholog_changes = Change.objects.filter(gene__entrez_id__in=orth_ids).exclude(organism=gene.organism)
    ortholog_changes = ChangeTable(Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(gene__entrez_id__in=orth_ids), order_by=request.GET.get('sort'), prefix='t_2_') 
    ortholog_changes.paginate(page=request.GET.get('page_t2', 1))

    resp = render_to_response('gene.html', {
        'title': '{} {}'.format(gene.name, '({})'.format(gene.symbol) if gene.symbol != '' else ''),
        'species_options': generate_species_options(request),
        'gene': gene,
        'unigene': unigene, 
        'table': table,
        'go': go,
        'orthologs': ortholog_list,
        'ortholog_changes': ortholog_changes,
        #'ortholog_changes': ortholog_tables,
        'use_sidebar': show_sidebar(request),
    }, context_instance=RequestContext(request))
    if show_sidebar(request):
        patch_cache_control(resp, no_cache=True, must_revalidate=True, max_age=0)
    return resp

def tissue(request, evid):
    tissue = get_object_or_404(Tissue, evid=evid)
    decendents = tissue.get_descendants(include_self=True)

    tissues = Tissue.objects.all().prefetch_related('change_set')
    tissues_with_count = Tissue.objects.add_related_count(tissues, Change, 'tissues', 'number_of_changes', cumulative=True)
    jtissues = {}
    for t in tissues_with_count:
        jtissues[t.name] = {'type_changes_count': 0, 'evid': t.evid, 'synonyms': t.synonyms, 'number_of_changes': 0, 'url': ''}
    for t in tissues_with_count:
        type_count = list(t.change_set.values('type').annotate(Count('type')))
        jtissues[t.name] = {'type_changes_count': type_count, 'evid': t.evid, 'synonyms': t.synonyms, 'number_of_changes': t.number_of_changes, 'url': '{0}?l=tissue&amp;lid={1}&amp;species[]={2}'.format(reverse('daa.atlas.views.results'), str(t.evid), 9606)}

    #table = ChangeTable(Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(tissues__evid=evid), order_by=request.GET.get('sort'))
    #table = ChangeTable(Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(tissues__in=decendents), order_by=request.GET.get('sort'))
    #table.paginate(page=request.GET.get('page', 1))
    
    changes = Change.objects.filter(tissues__in=decendents, gene__isnull=True).distinct().order_by('type', 'name')
    molecular_total = Change.objects.filter(tissues__in=decendents, type='molecular').count()
    grouped_changes = {}
    for c in changes:
        if c.type not in grouped_changes:
            grouped_changes[c.type] = []
        grouped_changes[c.type].append(c)
    
    resp = render_to_response('tissue.html', {
        'title': '{} age-related changes'.format(tissue.name.title()),
        'species_options': generate_species_options(request),
        'tissue': tissue,
        'change_count': changes.count(),
        'changes': grouped_changes,
        'molecular_total': molecular_total,
        #'table': table,
        #'nodes': Tissue.objects.all(),
        'use_sidebar': show_sidebar(request),
        'nodes': tissues_with_count,
        'jtissues': json.dumps(jtissues)
    }, context_instance=RequestContext(request))
    if show_sidebar(request):
        patch_cache_control(resp, no_cache=True, must_revalidate=True, max_age=0)
    return resp

def reference(request, id):
    ref = get_object_or_404(Reference, id=id)
    table = ChangeTable(Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(references__id=id), order_by=request.GET.get('sort'))
    table.paginate(page=request.GET.get('page', 1))
    resp = render_to_response('reference.html', {
        'title': 'The Digital Ageing Atlas | '+ref.title,
        'species_options': generate_species_options(request),
        'ref': ref,
        'table': table,
        'use_sidebar': show_sidebar(request),
    }, context_instance=RequestContext(request))
    if show_sidebar(request):
        patch_cache_control(resp, no_cache=True, must_revalidate=True, max_age=0)
    return resp

def return_as_json(request):
    return_type = request.GET.get('type')
    term = request.GET.get('term')
    id = request.GET.get('id')

    species = request.GET.getlist('species')

    species_list = []
    if len(species) > 0:
        for sp in species:
            species_list.append(Q(organism__taxonomy_id=sp))
    else:
        for sp in Organism.objects.all():
            species_list.append(Q(organism__taxonomy_id=sp.taxonomy_id))

    if return_type == 'stats' and term is not None:
        stats = [] 
        for species in Organism.objects.filter(hasDatabase=True):
            stats.append([{'name': species.common_name, 'id': species.taxonomy_id}, get_stats(term, species=[Q(organism__taxonomy_id=species.taxonomy_id)])])
        stats = sorted(stats, key=lambda x: x[0])
        return HttpResponse(json.dumps(stats))
    elif return_type == 'change' and id is not None:
        change = Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', '    gene').prefetch_related('tissues', 'properties').get(identifier=id)
        return HttpResponse(serializers.serialize('json',[change]))
    elif return_type == 'results' and term is not None:
        changes = ChangeFilterSet(request.GET, Change.objects.select_related('data__percentage', 'data__equation', 'data__dataset', 'organism', 'process_measured', 'gene').prefetch_related('tissues', 'properties').filter(reduce(operator.or_, species_list), change_query(term)))
        return HttpResponse(serializers.serialize('json',changes.qs))
    else:
        return Http404()

def saved(request, method):
    url = request.POST.get('url')
    id = request.POST.get('id')

    path_only = urlparse.urlparse(url)[2]
    match = resolve(path_only)
    expire_view_cache(match.view_name, args=match.kwargs.values(), key_prefix='atlaslive', method='POST')

    if 'saved' not in request.session:
        request.session['saved'] = {} 

    if method == 'add' and id not in request.session['saved']:
        change = Change.objects.get(identifier=id)
        request.session['saved'][id] = (change.name, change.type)
        request.session.modified = True
    elif method == 'remove' and id in request.session['saved']:
        del request.session['saved'][id]
        request.session.modified = True 
    elif method == 'clear':
        request.session['saved'] = []
        request.session.modified = True
    
    if len(request.session['saved']) < 1:
        del request.session['saved']

    return redirect(url) 
