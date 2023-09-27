import json
import csv
import StringIO

from django.contrib import admin
from django.conf.urls import *
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.db.models import Q, Count, Max
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers

from reversion.admin import VersionAdmin

from daa.gendr.models import Biblio, Gene, Expression, BiblioGene
from daa.atlas.admin_forms import ReferenceAdminForm
from daa.atlas.unicode_reader import UnicodeDictReader

from daa.atlas.admin_widgets import GeneLookupWidget

from daa.django_libage.fields import LibageReferencesField
from daa.django_libage.models import BibliographicEntry, Citation, Source, Tag

#
# GenDR
#
class BiblioInline(admin.TabularInline):
    model = BiblioGene 
    extra = 0
    verbose_name_plural = 'gene references'
    verbose_name = 'gene reference'

    raw_id_fields = ('biblio_id', )
    template = 'admin/tabular.html'

class GeneAdminForm(forms.ModelForm):
    libage_references = LibageReferencesField(attrs = {'name_fields': ['id_gene_symbol', 'id_gene_name', 'id_species_name'], 'source_id': Source.objects.filter(short_name='gendr')[0].id, 'database': 'gendr'}, required=False)
    identifier = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(GeneAdminForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            self.fields['libage_references'].initial = [kwargs['instance'].id]
            self.fields['identifier'].initial = kwargs['instance'].id
        else:
            max_auto = Gene.objects.all().aggregate(max=Max('id'))
            self.fields['identifier'].initial = max_auto['max']+1

    class Meta:
        model = Gene 
        widgets = {
            'entrez_id': GeneLookupWidget,
        }
        fields = '__all__'

class GeneAdmin(VersionAdmin):#admin.ModelAdmin):
    #inlines = (BiblioInline,)

    list_display = ('entrez_id', 'gene_symbol', 'gene_name', 'species_name',)
    list_display_links = ('entrez_id', 'gene_symbol', 'gene_name',)

    list_filter = ('species_name',)
    search_fields = ('gene_id', 'gene_symbol', 'gene_name', 'entrez_id', )

    form = GeneAdminForm

    class Media:
        js = ('js/admin_extensions.js', 'js/LibageReferencePopup.js', 'js/lookup.js')

    def check_name(self, obj):
        return u'<a href="../{0}">{1}</a>'.format(obj.id, obj.gene_symbol)
    check_name.allow_tags = True
    check_name.admin_order_field = 'gene_symbol'

    def queryset(self, request):
        qs = super(GeneAdmin, self).queryset(request)
        if 'check' in request.path:
            return qs.filter(Q(description='') | Q(species_name='') | Q(entrez_id=None) | Q(gene_symbol=''))
        return qs

    def get_urls(self):
        urls = super(GeneAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^check/$', self.admin_site.admin_view(self.check_errors), name='gene_manip_check'),
            url(r'^export/$', self.admin_site.admin_view(self.export), name='gendr_manip_export'),
        )
        return extra_urls + urls

    def export(self, request):
        from django.db import connections
        cursor = connections['gendr'].cursor()
        ocursor = connections['ortholog'].cursor()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=gendr_manipulations.csv'

        #cursor.execute("select genes.gene_symbol, genes.gene_id, genes.species_name, genes.description, genes.entrez_id, genes.gene_name, genes.function, group_concat(biblio.pubmed separator ',') from genes LEFT JOIN biblio_genes ON genes.entrez_id = biblio_genes.entrez_id LEFT JOIN biblio ON biblio.id_biblio = biblio_genes.biblio_id GROUP BY genes.entrez_id")
        cursor.execute("select genes.id, genes.gene_name, genes.gene_symbol, genes.alias, genes.species_name, genes.entrez_id, genes.ensembl, genes.description, genes.function from genes")

        genes = cursor.fetchall()

        writer = csv.writer(response)
        writer.writerow(['GenDR ID', 'name', 'symbol', 'aliases', 'organism', 'entrez gene id', 'ensembl', 'description', 'function', 'references', 'orthologs'])
        for row in genes:
            ref = Citation.objects.get(identifier=unicode(row[0]), source__short_name='gendr')
            references = [p.pubmed for p in ref.bibliographicentry_set.all() if p.pubmed is not None]

            output = list(row)
            '''
            cursor.execute("select distinct symbol, species from orthologs where orthologs.unique_grouping in (select t2.unique_grouping from orthologs as t2 where t2.entrez_id = "+str(row[4])+") GROUP BY orthologs.species, orthologs.symbol")
            orthologs = []
            for r in cursor.fetchall():
                orthologs.append(r[0]+';'+r[1])
            output.append(','.join(orthologs))
            '''
            orthologs = []
            if row[5] is not None:
                ocursor.execute("select * from ortholog where entrez_a = {entrez} or entrez_b = {entrez}".format(entrez=row[5]))
                for r in ocursor.fetchall():
                    if r[5] == row[4]:
                        orthologs.append('{};{}'.format(r[8],r[11]))
                    else:
                        orthologs.append('{};{}'.format(r[2],r[5]))

            output.append(','.join(references))
            output.append(','.join(orthologs))
            writer.writerow(output)

        return response 

    def check_errors(self, request):
        ChangeList = self.get_changelist(request)
        list_display = ['action_checkbox', 'id', 'check_name', 'species_name', 'issues']# 'identifier', 'check_name', 'type', 'organism', 'issues']
        list_display_links = ['check_name']
        cl = ChangeList(request, self.model, list_display, list_display_links, self.list_filter,self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
        cl.formset = None
        return render(request, 'admin/check_change_list.html', {
            'cl': cl,
            'app_label': self.opts.app_label, 
            'title': 'Check gene manipulations for errors',
        })
    
class ExpressionAdmin(VersionAdmin):
    list_display = ('entrez_id', 'gene_symbol', 'gene_name', 'overexp', 'underexp', 'total',)
    list_display_links = ('entrez_id', 'gene_symbol', 'gene_name',)

    list_filter = ('classification',)
    search_fields = ('entrez_id', 'gene_symbol', 'gene_name',)

    def get_urls(self):
        urls = super(ExpressionAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^export/$', self.admin_site.admin_view(self.export), name='gendr_exp_export'),
        )
        return extra_urls + urls

    def export(self, request):
        from django.db import connections
        cursor = connections['gendr'].cursor()
        ocursor = connections['ortholog'].cursor()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=gendr_expression.csv'

        cursor.execute("select gene_name,gene_symbol,alias,entrez_id,ensembl,total,overexp,underexp,p_value,classification from expression")

        genes = cursor.fetchall()

        writer = csv.writer(response)
        writer.writerow(['name', 'symbol', 'aliases', 'entrez gene id','ensembl','total','overexp','underexp','p_value','classification','orthologs'])
        for row in genes:
            '''
            cursor.execute("select distinct symbol, species from orthologs where orthologs.unique_grouping in (select t2.unique_grouping from orthologs as t2 where t2.entrez_id = "+str(row[2])+") GROUP BY orthologs.species, orthologs.symbol")
            orthologs = []
            for r in cursor.fetchall():
                orthologs.append(r[0]+';'+r[1])
            '''
            orthologs = []
            if row[3] is not None:
                ocursor.execute("select * from ortholog where entrez_a = {entrez} or entrez_b = {entrez}".format(entrez=row[3]))
                for r in ocursor.fetchall():
                    if r[5] == 'Mus musculus':
                        orthologs.append('{};{}'.format(r[8],r[11]))
                    else:
                        orthologs.append('{};{}'.format(r[2],r[5]))
            output = list(row)
            output.append(','.join(orthologs))
            writer.writerow(output)

        return response 

class BiblioAdmin(VersionAdmin):
    search_fields = ('title', 'author', 'journal', 'book_title', 'editor')

    form = ReferenceAdminForm

    class Media:
        js = ('js/lookup.js',)

    def check_name(self, obj):
        return u'<a href="../{0}">{1}</a>'.format(obj.id_biblio, obj)
    check_name.allow_tags = True
    check_name.admin_order_field = 'id_biblio'
    
    def queryset(self, request):
        qs = super(BiblioAdmin, self).queryset(request)
        if 'check' in request.path:
            return qs.annotate(has_genes=Count('bibliogene')).filter(Q(has_genes=0) | (Q(pubmed__isnull=False) & (Q(pages='') | Q(author='') | Q(title='') | Q(year__isnull=True))))
        return qs

    def get_urls(self):
        urls = super(BiblioAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^lookup/(?P<pubmed>\d+)/$', self.admin_site.admin_view(self.lookup)),
            url(r'^check/$', self.admin_site.admin_view(self.check), name='gendr_biblio_check'),
        )
        return extra_urls + urls
    
    def lookup(self, request, pubmed):
        fetch = FetchReference()
        results = fetch.fetchPubmed(pubmed)
        return HttpResponse(json.dumps(results))

    ''''def check(self, request):
        ChangeList = self.get_changelist(request)
        list_display = ['action_checkbox', 'check_name', 'issues']# 'identifier', 'check_name', 'type', 'organism', 'issues']
        list_display_links = ['check_name']
        cl = ChangeList(request, self.model, list_display, list_display_links, self.list_filter,self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
        cl.formset = None
        return render(request, 'admin/check_change_list.html', {
            'cl': cl,
            'app_label': self.opts.app_label, 
            'title': 'Check gene manipulations for errors',
        })
    '''
admin.site.register(Gene, GeneAdmin)
admin.site.register(Biblio, BiblioAdmin)
admin.site.register(Expression, ExpressionAdmin)
