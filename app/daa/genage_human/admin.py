import json
import csv
import StringIO
import os

from django.contrib import admin
from django.conf.urls import url, patterns
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.db.models import Q, Count, Max
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.conf import settings

from reversion.admin import VersionAdmin

from daa.genage_human.models import Name, Biblio, Features, Go, Homolog, Interaction, Links, Sequence
from daa.atlas.admin_widgets import SelectableForeignKeyRawIdWidget, EditForeignKeyRawIdWidget, GeneLookupWidget, ReferenceLookupWidget, GenageDetailsLookupWidget 
from daa.fetchscript.fetch import FetchGene, FetchReference, FetchDetails
from daa.atlas.admin_forms import ReferenceAdminForm
from daa.atlas.unicode_reader import UnicodeDictReader

from daa.django_libage.fields import LibageReferencesField
from daa.django_libage.models import BibliographicEntry, Citation, Source, Tag

#
# GenAge
#
class BiblioAdmin(VersionAdmin):

    search_fields = ('title', 'author', 'journal', 'book_title', 'editor', 'pubmed')

    form = ReferenceAdminForm

    actions = ['bulk_update_references']

    class Media:
        js = ('js/lookup.js',)

    def check_name(self, obj):
        return u'<a href="../{0}">{1}</a>'.format(obj.id_biblio, obj)
    check_name.allow_tags = True
    check_name.admin_order_field = 'id_biblio'
    
    def queryset(self, request):
        qs = super(BiblioAdmin, self).queryset(request)
        if 'check' in request.path:
            return qs.annotate(has_genes=Count('ref')).filter(Q(has_genes=0) | (Q(pubmed__isnull=False) & (Q(pages='') | Q(author='') | Q(title='') | Q(year__isnull=True))))
        return qs
    
    def get_urls(self):
        urls = super(BiblioAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^lookup/(?P<pubmed>\d+)/$', self.admin_site.admin_view(self.lookup)),
            url(r'^check/$', self.admin_site.admin_view(self.check_errors), name='genage_human_biblio_check'),
        )
        return extra_urls + urls
    
    def lookup(self, request, pubmed):
        fetch = FetchReference()
        results = fetch.fetchPubmed(pubmed)
        return HttpResponse(json.dumps(results))

    def check_errors(self, request):
        ChangeList = self.get_changelist(request)
        list_display = ['action_checkbox', 'check_name', 'issues']
        list_display_links = ['check_name']
        cl = ChangeList(request, self.model, list_display, list_display_links, self.list_filter,self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
        cl.formset = None
        return render(request, 'admin/check_change_list.html', {
            'cl': cl,
            'app_label': self.opts.app_label, 
            'title': 'Check GenAge human bibliogrpahy for errors',
        })

    def bulk_update_references(self, request, queryset):
        updated = 0
        total = 0
        for obj in queryset:
            total += 1
            if obj.pubmed != '':
                fetch = FetchReference()
                results = fetch.fetchPubmed(obj.pubmed)
                for item in results:
                    obj.__dict__[item] = results[item]
                obj.save()
                updated += 1
        self.message_user(request, '{0} of {1} references where updated'.format(updated, total))
    bulk_update_references.short_description = 'Get and update/fill in multiple reference details'

class ReferenceInline(admin.TabularInline):
    model = Name.refs.through
    extra = 0
    raw_id_fields = ('id_biblio', )
    verbose_name = 'Reference'
    verbose_name_plural = 'References'

    #template = 'admin/tabular.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return db_field.formfield(widget=EditForeignKeyRawIdWidget(db_field.rel, admin.site))

class FeaturesInline(admin.StackedInline):
    model = Features
    extra = 1
    max_num = 1
    verbose_name = 'Features'
    verbose_name_plural = 'Features'

class LinksInline(admin.StackedInline):
    model = Links
    extra = 1
    max_num = 1
    verbose_name = 'Links'
    verbose_name_plural = 'Links'

class SequenceInline(admin.StackedInline):
    model = Sequence
    extra = 1
    max_num = 1
    verbose_name = 'Sequence'
    verbose_name_plural = 'Sequences'

class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 1
    fk_name = 'hagrid_one'
    verbose_name = 'Interaction'
    verbose_name_plural = 'Interactions'

    #template = 'admin/tabular.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return db_field.formfield(widget=EditForeignKeyRawIdWidget(db_field.rel, admin.site))

class GoInline(admin.TabularInline):
    model = Go
    extra = 1 
    verbose_name = 'GO Term'
    verbose_name_plural = 'GO Terms'

    #template = 'admin/tabular.html'

class HomologInline(admin.TabularInline):
    model = Homolog
    extra = 0
    verbose_name = 'Homolog'
    verbose_name_plural = 'Homologs'

    #template = 'admin/tabular.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return db_field.formfield(widget=EditForeignKeyRawIdWidget(db_field.rel, admin.site))

class GenageHumanAdminForm(forms.ModelForm):
    libage_references = LibageReferencesField(attrs = {'name_fields': ['id_symbol_hugo', 'id_name_common'], 'source_id': Source.objects.filter(short_name='genage_human')[0].id, 'database': 'genage_human'})
    identifier = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(GenageHumanAdminForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            self.fields['libage_references'].initial = [str(kwargs['instance'].id_hagr).zfill(4)]
            self.fields['identifier'].initial = str(kwargs['instance'].id_hagr).zfill(4) 
        else:
            max_auto = Name.objects.all().aggregate(max=Max('id_hagr'))
            self.fields['identifier'].initial = str(max_auto['max']+1).zfill(4) 

    class Meta:
        widgets = {
            'entrez_id': GenageDetailsLookupWidget,
        }
        model = Name 
        fields = '__all__'
    
class GenAgeHumanAdmin(VersionAdmin):

    list_display = ('id_hagr', 'name_common', 'symbol_hugo', 'aliases')
    list_display_links = ('id_hagr', 'name_common')
    search_fields = ('name_common', 'symbol_hugo', 'aliases', 'id_hagr')

    inlines = (FeaturesInline, LinksInline, SequenceInline, InteractionInline, GoInline, HomologInline,)

    form = GenageHumanAdminForm

    class Media:
        js = ('js/lookup.js', 'js/admin_extensions.js', 'js/LibageReferencePopup.js',)
    
    def get_urls(self):
        urls = super(GenAgeHumanAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^lookup/(?P<entrezid>\d+)/(?P<lookup_section>.*)/$', self.admin_site.admin_view(self.lookup)),
            url(r'^import/$', self.admin_site.admin_view(self.csvimport), name='genage_human_csvimport'),
            url(r'^export/$', self.admin_site.admin_view(self.export), name='genage_human_export'),
        )
        return extra_urls + urls

    def csvimport(self, request):
        return None

    def export(self, request):
        from django.db import connections
        cursor = connections['genage_human'].cursor()
        ocursor = connections['ortholog'].cursor()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=genage_human.csv'

        cursor.execute("SELECT distinct names.id_hagr, names.name_common, names.symbol_hugo, names.aliases, names.entrez_id, links.ensembl, links.swissprot, links.unigene, features.why, features.band, features.location_start,features.location_end,features.orientation,sequences.acc_promoter,sequences.acc_orf,sequences.acc_cds FROM names LEFT JOIN features on features.hagrid = names.id_hagr LEFT JOIN links on links.hagrid = names.id_hagr LEFT JOIN sequences on sequences.hagrid = names.id_hagr LEFT JOIN refs ON refs.hagrid = names.id_hagr group by names.id_hagr") 

        genes = cursor.fetchall()

        writer = csv.writer(response, dialect='excel')
        writer.writerow(['GenAge ID', 'name', 'symbol', 'aliases','entrez gene id','ensembl', 'uniprot', 'why','band','location start','location end','orientation','acc promoter','acc orf','acc cds','references', 'orthologs'])
        for row in genes:
            ref = Citation.objects.get(identifier=unicode(row[0]).zfill(4), source__short_name='genage_human')
            references = [p.pubmed for p in ref.bibliographicentry_set.all() if p.pubmed is not None]

            #cursor.execute("select distinct symbol, species from orthologs where orthologs.unique_grouping in (select t2.unique_grouping from orthologs as t2 where t2.entrez_id = "+str(row[4])+")  and species != 'Homo sapiens' GROUP BY orthologs.species, orthologs.symbol")
            ocursor.execute("select * from ortholog where entrez_a = {entrez} or entrez_b = {entrez}".format(entrez=row[4]))
            orthologs = []
            for r in ocursor.fetchall():
                if r[5] == 'Homo sapiens':
                    orthologs.append('{};{}'.format(r[8],r[11]))
                else:
                    orthologs.append('{};{}'.format(r[2],r[5]))

            output = list(row)
            output.append(','.join(references))
            output.append(','.join(orthologs))
            writer.writerow(output)

        return response 

    def lookup(self, request, entrezid, lookup_section):
        MAPPING = { 
            'entrez_id': 'entrez_gene',
            'alias': 'aliases',
            'symbol': 'symbol_hugo',
            'name': 'name_common',
            'ensembl': 'links_set-0-ensembl',
            'uniprot': 'links_set-0-swissprot',
            'hprd': 'links_set-0-hprd',
            'unigene': 'links_set-0-unigene',
            'omim': 'links_set-0-omim',
            'homologene': 'links_set-0-homologene',
            'chromosome_location': 'features_set-0-band',
            'location_start': 'features_set-0-location_start',
            'location_end': 'features_set-0-location_end',
            'orientation': 'features_set-0-orientation',
            'description': 'features_set-0-phenotype',
            'seq_promotor': 'sequence_set-0-seq_promoter',
            'acc_promotor': 'sequence_set-0-acc_promotor',
            'seq_orf': 'sequence_set-0-seq_orf',
            'acc_orf': 'sequence_set-0-acc_orf',
            'seq_cds': 'sequence_set-0-seq_cds',
            'acc_cds': 'sequence_set-0-acc_cds',
        }

        f = FetchDetails(config_location=os.path.join(settings.ABSOLUTE_PATH, 'fetch.cfg'))
        results = {}

        if lookup_section == 'entrez':
            entrezd = f.fetchDetailsFromEntrez(entrezid) if not None else {}
            results = dict(entrezd.items())

        if lookup_section in ('uniprot', 'nucl'):
            uniprot = f.translateID(entrezid, 'P_ENTREZGENEID', 'ID')
            nuc = f.translateID(uniprot, 'ID', 'REFSEQ_NT_ID')

        if lookup_section == 'uniprot':
            uniprotd = {}
            if uniprot is not None:
                uniprotd = f.fetchDetailsFromUniProt(uniprot) if not None else {}
            results = dict(uniprotd.items())

        if lookup_section == 'nucl':
            nucd = {}
            if nuc is not None:
                nucd = f.fetchDetailsFromNucleotide(nuc) if not None else {}
            results = dict(nucd.items())

        #results = dict(uniprotd.items() + nucd.items() + entrezd.items())

        if lookup_section == 'interactions':
            interactions = f.fetchDetailsFromBioGrid(entrezid, 9606) #json.loads(f.fetchDetailsFromHPRD(entrezd['symbol']))
            results['interactions'] = []
            for i,interact in interactions.items():
                if interact['ENTREZ_GENE_A'] == unicode(entrezid):
                    interacts_with = interact['ENTREZ_GENE_B']
                else:
                    interacts_with = interact['ENTREZ_GENE_A']
                try:
                    g = Name.objects.get(entrez_id=interacts_with)
                    results['interactions'].append(g.id_hagr)
                except:
                    pass
            results['interactions'] = list(set(results['interactions']))

        orig = results.copy()
        for k in orig:
            if k in MAPPING:
                results[MAPPING[k]] = results[k]

        return HttpResponse(json.dumps(results))

admin.site.register(Name, GenAgeHumanAdmin)
admin.site.register(Biblio, BiblioAdmin)
