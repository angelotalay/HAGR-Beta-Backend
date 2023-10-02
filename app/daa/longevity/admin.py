# -*- encoding: utf-8 -*-

import copy
import csv
import StringIO
import json

from django.contrib import admin
from django.conf.urls import *
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from daa.longevity.models import *
from daa.fetchscript.fetch import FetchDetails
from daa.atlas.admin_widgets import SelectableForeignKeyRawIdWidget, EditForeignKeyRawIdWidget, GeneLookupWidget, ReferenceLookupWidget, DataForeignKeyRawIdWidget

from daa.atlas.unicode_reader import UnicodeDictReader

from daa.django_libage.models import BibliographicEntry, Citation, Tag, Source
from daa.fetchscript.fetch import FetchDetails, FetchReference

def duplicate_variant(modeladmin, request, queryset):
    for variant in queryset: 
        variant_copy = copy.copy(variant)
        variant_copy.id = None
        variant_copy.save()

duplicate_variant.short_description = 'Duplicate a variant for use when manually adding groups'

class VariantAdmin(admin.ModelAdmin):
    actions = [duplicate_variant]
    list_display = ('id', 'location', 'gene')
    search_fields = ('id', 'location', 'gene__name', 'gene__symbol',)

    raw_id_fields = ('gene', 'variantgroup',)

    class Media:
        js = ('js/lookup.js',)

    def get_urls(self):
        urls = super(VariantAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^clear_libage/$', self.admin_site.admin_view(self.clearlibage), name='longevity_clearlibage'),
            url(r'^import/$', self.admin_site.admin_view(self.csvimport), name='longevity_csvimport'),
            url(r'^export/$', self.admin_site.admin_view(self.export), name='longevity_csvexport'),
            url(r'^import/item/(?P<rid>\d+)/$', self.admin_site.admin_view(self.csvimportitem), name='longevity_csvimportitem'),
        )
        return extra_urls + urls

    def clearlibage(self, request):
        citations = Citation.objects.filter(source__short_name='longevity')
        citations.delete()
        return render(request, 'libage_deleted.html', {'title': 'Delete LongevityMap citations from LibAge', 'app_label': 'LongevityMap'})

    def export(self, request):
        from django.db import connections
        cursor = connections['longevity'].cursor()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=longevity.csv'
        response['Content-Encoding'] = 'UTF-8'
        response['Content-type'] = 'text/csv; charset=UTF-8'

        cursor.execute("""SELECT CASE WHEN count(variantgroup_id) > 1 THEN CONCAT('G',variantgroup_id) ELSE variantgroup_id END, p.name, v.association, group_concat(distinct identifier separator ',') as variants, group_concat(distinct g.symbol separator ',') as gene_symbol, v.study_design, v.conclusions, v.quickpubmed, group_concat(distinct v.location separator ',') as location from variant v left join population p on v.population_id = p.id left join gene g on v.gene_id = g.entrez_id group by variantgroup_id""")

        variants = cursor.fetchall()
        writer = csv.writer(response)

        writer.writerow(['id','population','association','variants', 'gene_symbol','study_design','conclusions','quickpubmed','location'])
        for row in variants:
            row = [(s.encode('utf8') if isinstance(s, basestring) else s) for s in row]
            row = ['' if s is None or s=='None' else s for s in row]
            writer.writerow(row)

        return response


    def csvimport(self, request):
        if len(request.FILES) > 0:
            f = request.FILES['datafile']
            for i, chunk in enumerate(f.chunks()):
                if chunk.startswith('\xef\xbb\xbf'):
                    chunk = chunk.strip('\xef\xbb\xbf')
                if i == 0:
                    headerline = chunk.split("\n",1)[0]
                else:
                    chunk = headerline + chunk
                #csvf = UnicodeDictReader(StringIO.StringIO(chunk), delimiter="\t")
                output = []
                for rid, r in enumerate(csv.DictReader(StringIO.StringIO(chunk), delimiter=",")):
                    output.append({'rid': rid, 'data': r})
            return render(request, 'import_complete.html', {'title': 'Import complete', 'app_label': 'LongevityMap', 'data': json.dumps(output)})
        return render(request, 'import_generic.html', {'title': 'Import into LongevityMap', 'app_label': 'LongevityMap'})

    @csrf_exempt
    def csvimportitem(self, request, rid):
        r = request.POST
        print r
        if r:
            print r
            print rid

            group = VariantGroup(association=r['association'])
            group.save()

            population, c = Population.objects.get_or_create(name=r['population'])

            ref = BibliographicEntry.objects.get_or_create_from_pubmed(r['pubmed'])

            short_ref = ref.get_short_reference()
            study_design = u"{}".format(r['study_design'])
            short_ref = u"{}".format(ref.get_short_reference())

            identifiers = r['variants'].split(',')
            genes = r['gene_symbol'].split(',')
            locations = r['location'].split(',')

            gene_count = 0;
            location = '';

            if (len(identifiers) == 0):
                location = r['location']
                variant = Variant(location=location,identifier=None,study_design=study_design, conclusions=r['conclusions'], association=r['association'], gene=None, population=population, quickref=short_ref, quickpubmed=ref.pubmed, quickyear=ref.year, variantgroup_id = group.id)
                variant.save()

            else:
                fd = FetchDetails()

                for n,i in enumerate(identifiers):

                    identifier = i.strip()
                    loc = ''
                    entrez_id = ''
                    gene = None

                    if identifier.startswith('rs'):
                        entrez_id = fd.fetchDetailsFromdbSNP(identifier)['entrez_id']
                    else:
                        entrez_id = fd.convertToEntrezGeneID(identifier)

                    if entrez_id == '' or entrez_id is None:
                        if len(genes) == 1:
                            entrez_id = fd.convertToEntrezGeneID(genes[0].strip())

                    if entrez_id == '' or entrez_id is None:
                        if len(genes) == len(identifiers):
                           entrez_id = fd.convertToEntrezGeneID(genes[n].strip())

                    if entrez_id != '' and entrez_id is not None:
                        gene_count += 1
                        gd = fd.fetchDetailsFromEntrez(entrez_id)
                        up = fd.translateID(entrez_id, 'P_ENTREZGENEID', 'ID')
                    
                        entrez_id = int(entrez_id.strip())
                        try:
                            gene = Gene(entrez_id=entrez_id, name=gd['name'], symbol=gd['symbol'], alias=gd['alias'], description=gd['description'], omim=gd['omim'], ensembl=gd['ensembl'], unigene=gd['unigene'], uniprot=up, cytogenetic_location=gd['chromosome_location'])
                            gene.save()
                            gene = Gene.objects.get(pk=gene.pk)
                        except IntegrityError as e:
                            print("Found record: " + str(entrez_id))
                            gene = Gene.objects.get(entrez_id=entrez_id)
                        
                        loc = gene.cytogenetic_location

                    if loc is None or loc == '':
                        if len(locations) == 1:
                            loc = locations[0].strip()

                    variant = Variant(location=loc, identifier=identifier,study_design=study_design, conclusions=r['conclusions'], association=r['association'], gene=gene, population=population, quickref=short_ref, quickpubmed=ref.pubmed, quickyear=ref.year, variantgroup = group)
                    variant.save()
  
                if gene_count > 1:
                    location = u'in {} genes'.format(gene_count)
                elif gene_count == 1:
                    location = genes[0]
                else:
                    location = r['location']

            variant.save()
            if len(identifiers) > 1:
                db_identifier = u'G'+str(group.id)
                ltype = u'group'
            else:
                db_identifier = str(variant.id)
                ltype = u'variant'

            title = u'{association} longevity {type} {location} for tested {population} population'.format(association=unicode(r['association']), type=unicode(ltype), location=unicode(location), population=unicode(population.name))
            source = Source.objects.get(short_name='longevity')
            cited = Citation(identifier=db_identifier, title=title, source=source)
            cited.save()
            ref.citations.add(cited)

            return HttpResponse('Complete', content_type="text/plain")

class VariantGroupAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__',)
    search_fields = ('id',)

class GeneAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'entrez_id': GeneLookupWidget,
        }

class GeneAdmin(admin.ModelAdmin):

    form = GeneAdminForm

    search_fields = ('entrez_id', 'symbol', 'name',)

    class Media:
        js = ('js/lookup.js',)
    
    def get_urls(self):
        urls = super(GeneAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^lookup/(?P<entrezid>\d+)/$', self.admin_site.admin_view(self.lookup)),
        )
        return extra_urls + urls

    def lookup(self, request, entrezid):
        fetch = FetchDetails()
        results = fetch.fetchDetailsFromEntrez(entrezid)
        return HttpResponse(json.dumps(results), content_type="application/json")

admin.site.register(Variant, VariantAdmin)
admin.site.register(VariantGroup, VariantGroupAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Population)
