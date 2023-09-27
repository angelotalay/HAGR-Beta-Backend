import json
import csv
import StringIO

from django.contrib import admin
from django.conf.urls import *
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.db.models import Q, F, Count, Max
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers

from reversion.admin import VersionAdmin

from daa.genage_model.models import Biblio, Model, Longevity
from daa.atlas.admin_widgets import SelectableForeignKeyRawIdWidget, EditForeignKeyRawIdWidget, GeneLookupWidget, ReferenceLookupWidget 
from daa.atlas.fetch import FetchGene, FetchReference, FetchDetails
from daa.atlas.admin_forms import ReferenceAdminForm
from daa.atlas.unicode_reader import UnicodeDictReader

from daa.django_libage.fields import LibageReferencesField
from daa.django_libage.models import BibliographicEntry, Citation, Source, Tag

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
            return qs.annotate(has_genes=Count('longevity')).filter(Q(has_genes=0) | (Q(pubmed__isnull=False) & (Q(pages='') | Q(author='') | Q(title='') | Q(year__isnull=True))))
        return qs
    
    def get_urls(self):
        urls = super(BiblioAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^lookup/(?P<pubmed>\d+)/$', self.admin_site.admin_view(self.lookup)),
            url(r'^check/$', self.admin_site.admin_view(self.check_errors), name='genage_model_biblio_check'),
        )
        return extra_urls + urls
    
    def lookup(self, request, pubmed):
        fetch = FetchReference()
        results = fetch.fetchPubmed(pubmed)
        return HttpResponse(json.dumps(results))

    def check_errors(request):
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

class GenageModelLongevityForm(forms.ModelForm):
    libage_references = LibageReferencesField(attrs = {'name_fields': ['id_symbol', 'id_name', 'id_organism'], 'source_id': Source.objects.filter(short_name='genage_model')[0].id, 'database': 'genage_model'})
    identifier = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(GenageModelLongevityForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            self.fields['libage_references'].initial = [kwargs['instance'].pk]
            self.fields['identifier'].initial = kwargs['instance'].pk
        else:
            max_auto = Longevity.objects.all().aggregate(max=Max('id'))
            self.fields['identifier'].initial = max_auto['max']+1

    class Meta:
        model = Longevity
        fields = '__all__'

class LongevityInline(admin.StackedInline):
    model = Longevity
    extra = 0

    #raw_id_fields = ('biblio', )
    exclude = ('biblio',)

    form = GenageModelLongevityForm

    #def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #    return db_field.formfield(widget=EditForeignKeyRawIdWidget(db_field.rel, admin.site))

class GenageModelAdminForm(forms.ModelForm): 
    class Meta:
        model = Model 
        widgets = {
            'entrez_id': GeneLookupWidget,
        }
        fields = '__all__'

class GenageModelAdmin(VersionAdmin):
    list_display = ('id_gene', 'symbol', 'name', 'organism')
    list_display_links = ('id_gene', 'symbol', 'name')
    list_filter = ('organism', )
    search_fields = ('name', 'symbol', 'organism', 'id_gene', 'entrez_id')

    inlines = (LongevityInline, )
    form = GenageModelAdminForm

    class Media:
        js = ('js/admin_extensions.js', 'js/LibageReferencePopup.js', 'js/lookup.js',)

    def check_name(self, obj):
        return u'<a href="../{0}">{1} {2}</a>'.format(obj.id_gene, obj.symbol, obj.name)
    check_name.allow_tags = True
    check_name.admin_order_field = 'name'

    def queryset(self, request):
        qs = super(GenageModelAdmin, self).queryset(request)
        if 'check' in request.path:
            return qs.annotate(long_count=Count('longevity'), long_bib_count=Count('longevity__biblio')).filter(Q(long_count=0) | Q(symbol='') | Q(long_bib_count=0) | Q(symbol=F('name')))
        return qs

    def get_urls(self):
        urls = super(GenageModelAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^check/$', self.admin_site.admin_view(self.check_errors), name='genage_model_checks'),
            url(r'^import/$', self.admin_site.admin_view(self.csvimport), name='genage_csvimport'),
            url(r'^import/complete$', self.admin_site.admin_view(self.csvimportcomplete), name='genage_csvimportcomplete'),
            url(r'^update/$', self.admin_site.admin_view(self.csvupdate), name='genage_csvupdate'),
            url(r'^update/complete$', self.admin_site.admin_view(self.csvupdatecomplete), name='genage_csvupdatecomplete'),
            url(r'^export/$', self.admin_site.admin_view(self.export), name='genage_models_export'),
        )
        return extra_urls + urls

    def export(self, request):
        from django.db import connections
        cursor = connections['genage_model'].cursor()
        ocursor = connections['ortholog'].cursor()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=genage_models.csv'

        cursor.execute("SELECT DISTINCT (select count(*) from longevity as l2 where l2.gene_id = models.id_gene and lifespan_effect = 'increase') as increase_count, (select count(*) from longevity as l2 where l2.gene_id = models.id_gene and lifespan_effect = 'decrease') as decrease_count, (select count(*) from longevity as l where l.longevity_influence='anti' and models.id_gene = l.gene_id) as anti_count, (select count(*) from longevity as l where l.longevity_influence ='pro' and models.id_gene = l.gene_id ) as pro_count, id_gene, name, symbol, alias, organism, entrez_id, ensembl, uniprot, unigene, functions, (select max(avg_lifespan_change) from longevity as l1 where models.id_gene = l1.gene_id having (increase_count > 0 and decrease_count = 0) or (increase_count = 0 and decrease_count > 0)) as max_avg_lifespan_change, lifespan_effect, longevity_influence, avg_lifespan_change, max_lifespan_change, longevity.id as lid FROM models LEFT JOIN longevity ON models.id_gene = longevity.gene_id") 

        writer = csv.writer(response)
        writer.writerow(['GenAge ID', 'name', 'symbol', 'aliases', 'organism', 'entrez gene id', 'ensembl', 'uniprot', 'unigene', 'functions', 'avg lifespan change (max obsv)', 'lifespan effect', 'longevity influence', 'observations', 'orthologs'])

        grouped = {}

        for row in cursor.fetchall():
            if row[4] not in grouped:
                grouped[row[4]] = []
            grouped[row[4]].append(list(row))

        for hagrid,entries in grouped.iteritems():
            observations = ''
            for e in entries:
                try:
                    ref = Citation.objects.get(identifier=e[-1], source__short_name='genage_model')
                    pubmed = ref.bibliographicentry_set.all()[0].pubmed
                except:
                    pubmed = ''
                observations += u'{0};{1};{2};{3};{4}|'.format(row[15] if row[15] is not None else '', row[16] if row[16] is not None else '', row[17] if row[17] is not None else '', row[18] if row[18] is not None else '', pubmed)

            row = entries[0]
            output = list(row[4:15])

            if row[0] > 0 and row[1] == 0:
                output.append('Increase')
            elif row[1] > 0 and row[0] == 0:
                output.append('Decrease')
            elif row[0] > 0 and row[1] > 0:
                output.append('Increase and Decrease')
            else:
                output.append('')

            if row[3] > 0 and row[2] == 0:
                output.append('Pro-Longevity')
            elif row[2] > 0 and row[3] == 0:
                output.append('Anti-Longevity')
            elif row[2] > 0 and row[3] > 0:
                output.append('Unclear')
            elif row[2] == 0 and row[3] == 0:
                output.append('Unannotated')
            else:
                output.append('')

            output.append(observations.rstrip('|'))

            orthologs = []
            if output[5] is not None:
                ocursor.execute("select * from ortholog where entrez_a = {entrez} or entrez_b = {entrez}".format(entrez=output[5]))
                for r in ocursor.fetchall():
                    if r[5] == output[4]:
                        orthologs.append('{};{}'.format(r[8],r[11]))
                    else:
                        orthologs.append('{};{}'.format(r[2],r[5]))

            output.append(','.join(orthologs))
            writer.writerow(output)

        return response 

    def check_errors(self, request):
        ChangeList = self.get_changelist(request)
        list_display = ['action_checkbox', 'check_name', 'organism', 'issues']
        list_display_links = ['check_name']
        cl = ChangeList(request, self.model, list_display, list_display_links, self.list_filter,self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
        cl.formset = None
        return render(request, 'admin/check_change_list.html', {
            'cl': cl,
            'app_label': self.opts.app_label, 
            'title': 'Check model organisms for errors',
        })
    
    VALID_HEADERS_MODEL = (
        'entrez_id',
        'name',
        'symbol',
        'organism',
        'alias',
    )
    VALID_HEADERS_LONG = (
        'avg_lifespan_change_desc',
        'max_lifespan_change_desc',
        'avg_lifespan_change',
        'lifespan_effect',
        'longevity_influence',
        'max_lifespan_change',
        'phenotype_description',
        'hidden',
        'pubmed',
        'method',
        'notes',
    )

    def append_record(self, record):
        '''
        try:
            biblio = Biblio.objects.get(pubmed=record['pubmed'])
        except Biblio.DoesNotExist:
            fetch = FetchReference()
            results = fetch.fetchPubmed(record['pubmed'])
            biblio = Biblio(**results)
            biblio.save()
        '''
        gene = Model.objects.get(entrez_id=int(record['entrez_id']))
        ld = dict((k,v) for (k,v) in record.iteritems() if k in self.VALID_HEADERS_LONG and k != 'pubmed')
        lng = Longevity(gene=gene, **ld)
        lng.save()

        title = u'{}, {} ({})'.format(gene.symbol, gene.name, gene.organism)
        ref = BibliographicEntry.objects.get_or_create_from_pubmed(pubmed=record['pubmed'])
        source = Source.objects.get(short_name='genage_model')
        citation = Citation(identifier=lng.id, title=title, source=source) 
        citation.save()
        ref.citations.add(citation)

    def csvimportcomplete(self, request):
        data = json.loads(request.POST['data'])
        # adding new genes
        for record in data['new']:
            try: 
                Model.objects.get(entrez_id=int(record['entrez_id']))
                self.append_record(record)
            except Model.DoesNotExist:
                '''
                try:
                    biblio = Biblio.objects.get(pubmed=record['pubmed'])
                except Biblio.DoesNotExist:
                    fetch = FetchReference()
                    results = fetch.fetchPubmed(record['pubmed'])
                    biblio = Biblio(**results)
                    biblio.save()
                '''

                f = FetchDetails()
                gene_info = f.fetchDetailsFromEntrez(record['entrez_id']) 
                    
                gd = dict((k,v) for (k,v) in record.iteritems() if k in self.VALID_HEADERS_MODEL and k != 'symbol' and k != 'name')
                ld = dict((k,v) for (k,v) in record.iteritems() if k in self.VALID_HEADERS_LONG and k != 'pubmed')
                gene = Model(symbol=gene_info['symbol'], name=gene_info['name'], **gd)
                gene.save()
                lng = Longevity(gene=gene, **ld)
                lng.save()

                title = u'{}, {} ({})'.format(gene.symbol, gene.name, gene.organism)
                ref = BibliographicEntry.objects.get_or_create_from_pubmed(pubmed=record['pubmed'])
                source = Source.objects.get(short_name='genage_model')
                citation = Citation(identifier=lng.id, title=title, source=source) 
                citation.save()
                ref.citations.add(citation)


        for record in data['append']:
            record = record[0]
            self.append_record(record)
            
        return render(request, 'admin/import_complete.html',  {'title': 'Import model organisms into GenAge: Successfull import', 'app_label': 'GenAge Model Organisms'})

    def csvimport(self, request):
        REQUIRED_HEADERS = set((
            'entrez_id',
            #'symbol',
            'organism',
            'pubmed',
        ))
        if len(request.FILES) > 0:
            f = request.FILES['datafile']
            op = {'append': [], 'duplicate': [], 'new': [], 'ignore': []}
            headerline = ''
            existing = {}
            for i, chunk in enumerate(f.chunks()):
                # Each chunk may not have the header, so find out what it is and store it
                if chunk.startswith('\xef\xbb\xbf'):
                    chunk = chunk.strip('\xef\xbb\xbf')
                if i == 0:
                    headerline = chunk.split("\n",1)[0]
                else:
                    chunk = headerline + chunk 
                csvf = UnicodeDictReader(StringIO.StringIO(chunk), delimiter="\t")
                invalid_fields = {}
                for line in csvf:
                    # check for required fields
                    valid_fields = {}
                    for fld in line:
                        if fld == 'hidden':
                            if line[fld] == '1':
                                line[fld] = True
                            else:
                                line[fld] = False
                        if (fld in self.VALID_HEADERS_MODEL or fld in self.VALID_HEADERS_LONG) and line[fld] != '' and line[fld] is not None:
                            if fld == 'lifespan_effect' or fld == 'longevity_influence':
                                line[fld] = line[fld].lower()
                            valid_fields[fld] = line[fld]
                        elif line[fld] != '' and line[fld] is not None:
                            invalid_fields[fld] = line[fld]

                    hdr = set(valid_fields.keys())

                    if REQUIRED_HEADERS < hdr:
                        try:
                            existing_gene = Model.objects.get(entrez_id=valid_fields['entrez_id'], organism=valid_fields['organism'])
                            diff_symbols = ''
                            if 'symbol' in valid_fields and existing_gene.symbol != valid_fields['symbol']:
                                diff_symbols = existing_gene.symbol
                            is_duplicate = False
                            for l in existing_gene.longevity_set.all():
                                try:
                                    c = Citation.objects.get(identifier=l.id, source__short_name='genage_model')
                                    if int(valid_fields['pubmed']) in [b.pubmed for b in c.bibliographicentry_set.all()]:
                                        #print existing_gene, existing_gene.id_gene
                                        op['duplicate'].append([valid_fields, existing_gene.id_gene, diff_symbols])
                                        is_duplicate = True
                                except:
                                    pass
                            if not is_duplicate:
                                op['append'].append([valid_fields, serializers.serialize('json', [existing_gene], ensure_ascii=False), diff_symbols])
                        except Model.DoesNotExist:
                            op['new'].append(valid_fields)
                    else:
                        op['ignore'].append(valid_fields)
            return render(request, 'admin/import_checks.html', {'title': 'Check changes of data to import', 'invalid_fields': invalid_fields, 'op': op, 'data': json.dumps(op), 'app_label': 'GenAge Model Organisms'})
        return render(request, 'admin/import.html', {'title': 'Import model organisms into GenAge', 'app_label': 'GenAge Model Organisms'}) 

    def csvupdate(self, request):
        REQUIRED_HEADERS = set((
            'longevity_id',
            'pubmed',
        ))
        if len(request.FILES) > 0:
            f = request.FILES['datafile']
            op = {'update': [], 'ignore': []}
            headerline = ''
            existing = {}
            for i, chunk in enumerate(f.chunks()):
                # Each chunk may not have the header, so find out what it is and store it
                if chunk.startswith('\xef\xbb\xbf'):
                    chunk = chunk.strip('\xef\xbb\xbf')
                if i == 0:
                    headerline = chunk.split("\n",1)[0]
                else:
                    chunk = headerline + chunk 
                csvf = UnicodeDictReader(StringIO.StringIO(chunk), delimiter="\t")
                invalid_fields = {}
                for line in csvf:
                    # check for required fields
                    valid_fields = {}
                    for fld in line:
                        if fld == 'hidden':
                            if line[fld] == '1':
                                line[fld] = True
                            else:
                                line[fld] = False
                        if (fld in self.VALID_HEADERS_MODEL or fld in self.VALID_HEADERS_LONG) and line[fld] != '' and line[fld] is not None:
                            if fld == 'lifespan_effect' or fld == 'longevity_influence':
                                line[fld] = line[fld].lower()
                            valid_fields[fld] = line[fld]
                        elif line[fld] != '' and line[fld] is not None:
                            invalid_fields[fld] = line[fld]

                    hdr = set(valid_fields.keys())

                    if REQUIRED_HEADERS < hdr:
                        op['update'].append(valid_fields)
                    else:
                        op['ignore'].append(valid_fields)
            return render(request, 'admin/update_checks.html', {'title': 'Check changes of data to update', 'invalid_fields': invalid_fields, 'op': op, 'data': json.dumps(op), 'app_label': 'GenAge Model Organisms'})
        print 'this is loading'
        return render(request, 'admin/update.html', {'title': 'Update longevity entries in GenAge', 'app_label': 'GenAge Model Organisms'}) 

    def csvupdatecomplete(self, request):
        data = json.loads(request.POST['data'])
        # adding new genes
        for record in data['update']:
            try:
                biblio = Biblio.objects.get(pubmed=record['pubmed'])
            except GenageModelBiblio.DoesNotExist:
                fetch = FetchReference()
                results = fetch.fetchPubmed(record['pubmed'])
                biblio = Biblio(**results)
                biblio.save()
                
            ld = dict((k,v) for (k,v) in record.iteritems() if k in self.VALID_HEADERS_LONG and k != 'pubmed')

            lng = Longevity.objects.get(id=data['longevity_id'])
            for k,v in ld:
                setattr(lng, k, v)
            lng.save()

        return render(request, 'admin/update_complete.html',  {'title': 'Update model organisms into GenAge: Sucessfull update', 'app_label': 'GenAge Model Organisms'})
                            

class LongevityAdmin(VersionAdmin):
    list_display = ('id', 'gene', 'phenotype_description', 'lifespan_effect', 'longevity_influence', )

admin.site.register(Longevity, LongevityAdmin)
admin.site.register(Model, GenageModelAdmin)
admin.site.register(Biblio, BiblioAdmin)
