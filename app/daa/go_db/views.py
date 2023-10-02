import operator

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import Http404
from django.db.models import Q

from daa.atlas.tables import ChangeTable
from daa.atlas.filters import ChangeFilterSet
from daa.atlas.view_functions import generate_species_options, get_stats, generate_filter_field_list, show_sidebar

from daa.go_db.models import *
from daa.atlas.models import Change, Gene

def test(request):
	
	for item in Association.objects.select_related().filter(gene_product__symbol='IGF1', gene_product__species__ncbi_taxa_id='9606'):
		print item.gene_product
		print item.term

	return render_to_response('index.html', {
			'title': 'GODB TESTPAGE',
		}, context_instance=RequestContext(request))

def index(request):
	return render_to_response('goterms.html', {
		'title': 'GO Term Tools',
		'species_options': generate_species_options(request),
	}, context_instance=RequestContext(request))

def go_to_changes(request):
	
	id = request.GET.get('id')

	gene_assoc = Association.objects.filter(term__acc=id).values('gene_product__symbol', 'gene_product__species__ncbi_taxa_id')
	if gene_assoc.count() > 0:
		genes = Gene.objects.filter(reduce(operator.or_, map(lambda x: Q(symbol=x['gene_product__symbol'], organism__taxonomy_id=x['gene_product__species__ncbi_taxa_id']), gene_assoc)))
		changes = Change.objects.filter(gene__in=genes)
		fltr = ChangeFilterSet(request.GET, queryset=changes)
		table = ChangeTable(fltr.qs, order_by=request.GET.get('sort'))
		table.paginate(page=request.GET.get('page', 1))

		fields = generate_filter_field_list(fltr, request)
		template = 'results.html'
	else:
		template = 'no_results.html'
		table = None

	return render_to_response(template, {
		'title': '{0} to corresponding changes'.format(id),
		'species_options': generate_species_options(request),
		'table': table,
        'use_sidebar': show_sidebar(request, True),
        'keys': ('s', 't', 'species[]', 'l', 'lid', 'page', 'sort'),
        'fields': fields,
	}, context_instance=RequestContext(request))
