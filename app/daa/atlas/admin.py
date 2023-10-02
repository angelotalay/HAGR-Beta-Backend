import json
import csv
import StringIO

from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.admin import GenericTabularInline
from django.conf.urls import *
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.db.models import Q, Count
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core import serializers
from django.db import models, transaction, router
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.util import unquote, flatten_fieldsets, get_deleted_objects, model_format_dict
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.middleware import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from django.contrib.admin.views.main import ChangeList

from mptt.admin import MPTTModelAdmin

from reversion.admin import VersionAdmin

from suit.widgets import AutosizedTextarea

from daa.atlas.models import *
from daa.genage_human.models import Name as GenageName
from daa.genage_model.models import Model as GenageModel
from admin_widgets import SelectableForeignKeyRawIdWidget, EditForeignKeyRawIdWidget, GeneLookupWidget, ReferenceLookupWidget, DataForeignKeyRawIdWidget 
from fetch import FetchGene, FetchReference
from daa.fetchscript.fetch import FetchDetails
from daa.atlas.admin_forms import ReferenceAdminForm
from daa.atlas.unicode_reader import UnicodeDictReader

from daa.django_libage.fields import LibageReferencesField
from daa.django_libage.models import BibliographicEntry, Citation, Source, Tag

csrf_protect_m = method_decorator(csrf_protect)

class TissueInline(admin.TabularInline):
    model = Change.tissues.through
    extra = 0
    raw_id_fields = ('tissue',)
    verbose_name = 'Tissue'
    verbose_name_plural = 'Tissues'

    #template = 'admin/tabular.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return db_field.formfield(widget=EditForeignKeyRawIdWidget(db_field.rel, admin.site))

class PropertyInline(admin.TabularInline):
    model = Change.properties.through
    extra = 0
    raw_id_fields = ('property',)
    verbose_name = 'Property'
    verbose_name_plural = 'Properties'

    #template = 'admin/tabular.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return db_field.formfield(widget=EditForeignKeyRawIdWidget(db_field.rel, admin.site))

class NotesInline(GenericTabularInline):
    model = Note 
    extra = 0

class ImageInline(admin.TabularInline):
    model = Image
    extra = 0
    verbose_name = 'Image'
    verbose_name_plural = 'Images'

class ChangeForm(forms.ModelForm):
    libage_references = LibageReferencesField(attrs={'name_fields': ['id_name'], 'source_id': 4, 'database': settings.LIBAGE_DATABASE})

    def __init__(self, *args, **kwargs):
        super(ChangeForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            self.fields['libage_references'].initial = [kwargs['instance'].identifier] 

    class Meta:
        model = Change
        fields = '__all__'

class ChangeAdmin(VersionAdmin):
    
    class Media:
        js = ('js/admin_extensions.js', 'js/LibageReferencePopup.js',) 

    fieldsets = (
        ('Basic Details', {
            'fields': ('identifier', 'name', 'type', 'starts_age', 'ends_age', 'time_measure', 'gender', 'organism', 'description')
        }),
        ('Gene', {
            'fields': ('gene',)
        }),
        ('Measurements of changes and datasets', {
            'fields': ('process_measured', 'data', ),
        }),
        ('Database only', {
            'description': 'These settings are not shown in the interface but may affect it',
            'classes': ('collapse',),
            'fields': ('hide', 'people'),
        }),
        ('References', {
            'fields': ('libage_references',),
        }),
    )

    form = ChangeForm

    raw_id_fields = ('gene', 'data')
    filter_horizontal = ('properties', 'people')
    inlines = (TissueInline, PropertyInline, NotesInline, ImageInline, )
    #exclude = ('references',)

    list_display = ('identifier', 'name', 'type', 'organism', 'hide', )
    list_display_links = ('identifier', 'name',) 
    list_filter = ('type', 'organism', 'hide', )
    search_fields = ('identifier', 'name',)

    actions = ['mark_hidden']

    def check_name(self, obj):
        return u'<a href="../{0}">{1}</a>'.format(obj.id, obj.name)
    check_name.allow_tags = True
    check_name.admin_order_field = 'name'

    def queryset(self, request):
        qs = super(ChangeAdmin, self).queryset(request)
        if 'check_references' in request.path:
            all_changes = Change.objects.all()
            citations = Citation.objects.filter(source__short_name=settings.LIBAGE_DATABASE).values_list('identifier', flat=True) 
            issues = []
            for c in all_changes:
                if c.identifier not in citations:
                    issues.append(c.identifier)
            return qs.filter(identifier__in=issues)
        elif 'check' in request.path:
            return qs.annotate(tissue_count=Count('tissues'), gene_count=Count('gene')).filter(Q(tissue_count=0) | Q(name='') | ((Q(type='physiological') | Q(type='psychological')) & Q(description='')) | (Q(gene_count__gt=0) & (Q(gene__symbol='') | Q(gene__name=''))))
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'data':
            return db_field.formfield(widget=DataForeignKeyRawIdWidget(db_field.rel, admin.site))
        else:
            return db_field.formfield(widget=EditForeignKeyRawIdWidget(db_field.rel, admin.site))
        return super(ChangeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def mark_hidden(self, request, queryset):
        queryset.update(hide=True)
    mark_hidden.short_description = 'Hide checked changes from DAA'

    def get_urls(self):
        urls = super(ChangeAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^check/$', self.admin_site.admin_view(self.check_errors), name="atlas_check"),
            url(r'^check_references/$', self.admin_site.admin_view(self.check_references), name="atlas_check_references"),
            url(r'^import/$', self.admin_site.admin_view(self.import_changes), name='atlas_import_changes'),
            url(r'^import/complete/$', self.admin_site.admin_view(self.import_changes_complete), name='atlas_import_changes_complete'),
            url(r'^import/item/$', self.admin_site.admin_view(self.ajax_import_change), name='atlas_ajax_import_change'),
            #url(r'^add_reference/$', self.admin_site.admin_view(self.add_reference), name='add_reference'),
        )
        return extra_urls + urls
    
    def check_errors(self, request):
        ChangeList = self.get_changelist(request)
        list_display = ['action_checkbox', 'identifier', 'check_name', 'type', 'organism', 'issues']
        list_display_links = ['check_name']
        cl = ChangeList(request, self.model, list_display, list_display_links, self.list_filter,self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
        cl.formset = None
        return render_to_response('admin/check_change_list.html', {
            'cl': cl,
            'app_label': self.opts.app_label, 
            'title': 'Check changes for errors',
        }, context_instance=RequestContext(request))


    def check_references(self, request):

        #ChangeList = self.get_changelist(request)
        list_display = ['action_checkbox', 'identifier', 'check_name', 'type', 'organism', 'hide']
        list_display_links = ['check_name']
        cl = ChangeList(request, self.model, list_display, list_display_links, self.list_filter,self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
        cl.formset = None
        return render_to_response('admin/change_list.html', {
            'cl': cl,
            'app_label': self.opts.app_label, 
            'title': 'Check changes for referencing errors',
        }, context_instance=RequestContext(request))

    REQUIRED = (
        'name',
        'type',
        'starts_age',
        'ends_age',
        'organism',
        'tissues',
        'pubmed',
    )

    VALID = (
        'gender',
        'description',
        'time_measure',
        'entrez_id',
        'properties',
    )

    VALID_CHANGE = (
        'name',
        'type',
        'starts_age',
        'ends_age',
        'type',
        'gender',
        'description',
        'time_measure',
    )
    
    VALID_DATA = (
        'process_measured',
        'is_negative',
        'sample_size',
        'measure',
        'method_collection',
        'data_transforms',
        'p_value',
    )

    REQUIRED_PERCENTAGE = (
        'type',
        'process_measured',
        'percentage_change',
    )

    REQUIRED_EQUATION = (
        'type',
        'plot',
        'coefficiant',
        'intercept'
        'percentage_change',
        'process_measured',
    )

    VALID_HEADERS = REQUIRED + VALID + VALID_DATA + REQUIRED_PERCENTAGE + REQUIRED_EQUATION 

    def import_changes(self, request):
        if len(request.FILES) > 0 :
            f = request.FILES['datafile']
            op = {'new': [], 'ignore': []}
            headerline = ''
            existing = {}
            for i, chunk in enumerate(f.chunks()):
                if chunk.startswith('\xef\xbb\xbf'):
                    chunk = chunk.strip('\xef\xbb\xbf')
                if i == 0:
                    headerline = chunk.split("\n",1)[0]
                else:
                    chunk = headerline + chunk
                csvf = UnicodeDictReader(StringIO.StringIO(chunk), delimiter="\t")
                invalid_fields = {}
                for line in csvf:
                    valid_fields = {}
                    required_headers = None
                    for fld in line:
                        if fld in self.VALID_HEADERS and line[fld] != '' and line[fld] is not None:
                            valid_fields[fld] = line[fld]
                        elif line[fld] != '' and line[fld] is not None:
                            invalid_fields[fld] = line[fld]

                    if 'coefficiant' in valid_fields:
                        required_headers = set(self.REQUIRED + self.REQUIRED_EQUATION)
                    elif 'percentage_change' in valid_fields:
                        required_headers = set(self.REQUIRED + self.REQUIRED_PERCENTAGE)
                    else:
                        required_headers = set(self.REQUIRED)

                    if 'is_negative' in valid_fields:
                        if valid_fields['is_negative'] == '1':
                            valid_fields['is_negative'] = True
                        else:
                            valid_fields['is_negative'] = False

                    hdr = set(valid_fields.keys())

                    tissues = valid_fields['tissues'].split(',')

                    if required_headers < hdr:
                        try:
                            for t in tissues:
                                r = Tissue.objects.get(name=t)
                            op['new'].append(valid_fields)
                        except Tissue.DoesNotExist:
                            op['ignore'].append([valid_fields, 'Tissue does not exist'])
                    else:
                        op['ignore'].append(valid_fields)
            return render(request, 'admin/import_check_changes.html', {
                'title': 'Check changes to be imported',
                'header': hdr,
                'invalid_fields': invalid_fields,
                'op': op,
                'data': json.dumps(op),
                'app_label': 'Digital Ageing Atlas'
            })
        return render(request, 'admin/import_changes.html', {
            'title': 'Check changes to be imported',
            'app_label': 'Digital Ageing Atlas'
        })

    def import_changes_complete(self, request):
        d = json.loads(request.POST['data'])
        return render(request, 'admin/import_changes_complete.html', {
            'title': 'Change import complete',
            'app_label': 'Digital Ageing Atlas',
            #'created': created,
            'data': json.dumps(d),
            'csrftoken': csrf.get_token(request),
        })

    def ajax_import_change(self, request):
        record = json.loads(request.POST.get('item'))
        created = {}
        
        # Get gene, add if does not exist
        # Get ref, add to LibAge database
        # Create an equation value (if required)
        # Get the tissue to be used
        # Create a change, add in the details
        gene = None
        data = None
        if 'entrez_id' in record:
            try:
                gene = Gene.objects.get(entrez_id=record['entrez_id'])
            except:
                fgene = FetchGene()
                results = fgene.fetchEntrez(record['entrez_id'])
                organism = Organism.objects.get(common_name=results['species'].title())
                del results['species']
                gene = Gene(organism=organism, **results)
                gene.save()
        if 'coefficiant' in record:
            eq = {k:v for k,v in record.iteritems() if k in (self.REQUIRED_EQUATION + self.VALID_DATA) and k not in ('type', 'process_measured',)}
            data = Equation(**eq)
            data.save()
        elif 'percentage_change' in record:
            eq = {k:v for k,v in record.iteritems() if k in self.REQUIRED_PERCENTAGE + self.VALID_DATA and k not in ('type', 'process_measured',)}
            data = Percentage(**eq)
            data.save()
        try:
            process_measured = ProcessMeasured.objects.get(name=record['process_measured'])
        except KeyError:
            process_measured = None

        try:
            organism = Organism.objects.get(common_name=record['organism'].title())
        except KeyError:
            organism = Organism.objects.get(common_name='Human')

        ch = {k:v for k,v in record.iteritems() if k in self.VALID_CHANGE}
        c = Change(gene=gene, organism=organism, data=data, process_measured=process_measured, **ch)
        c.save()
        created = {'id': c.id, 'identifier': c.identifier, 'name': c.name}
        for t in record['tissues'].split(','):
            c.tissues.add(Tissue.objects.get(name=t))

        if 'properties' in record:
            try:
                for p in record['properties'].split(','):
                    c.properties.append(Property.objects.get(name=p))
            except:
                pass

        # Adding stuff to LibAge
        try:
            b = BibliographicEntry.objects.get(pubmed=record['pubmed'])
        except ObjectDoesNotExist:
            fref = FetchReference()
            results = fref.fetchPubmed(record['pubmed'])
            del results['author_initials']
            b = BibliographicEntry(**results)
            b.save()
            b = BibliographicEntry.objects.get(pubmed=record['pubmed'])

        source = Source.objects.get(short_name=settings.LIBAGE_DATABASE) 
        citation,c = Citation.objects.get_or_create(identifier=c.identifier, title=c.name, source=source)
        b.citations.add(citation)

        return HttpResponse(json.dumps(created))

class TissueAdmin(MPTTModelAdmin, VersionAdmin):
    list_display = ('name', 'synonyms',)
    search_fields = ('name', 'synonyms',)
    list_per_page = 1000

class GeneAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'entrez_id': GeneLookupWidget,
        }

class GeneAdmin(VersionAdmin):#admin.ModelAdmin):
    list_display = ('entrez_id', 'symbol', 'name', 'organism', 'in_genage')
    list_display_links = ('entrez_id', 'symbol', 'name')
    list_filter = ('organism', 'in_genage')
    search_fields = ('entrez_id', 'symbol', 'name')

    form = GeneAdminForm

    class Media:
        js = ('js/lookup.js',)
    
    def get_urls(self):
        urls = super(GeneAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^lookup/(?P<entrezid>\d+)/$', self.admin_site.admin_view(self.lookup)),
            url(r'^genage/$', self.admin_site.admin_view(self.genage), name="atlas_check_genage")
        )
        return extra_urls + urls
    
    def genage(self, request):

        # Check human genes:
        humangenes = GenageName.objects.all()
        # Check model genes:
        models = Organism.objects.filter(hasDatabase=True).only('name').values()
        modelgenes = GenageModel.objects.filter(organism__in=map(lambda x: x['name'], models))

        matches = []
        for gene in humangenes:
            entrezid = gene.entrez_id
            try:
                exists = Gene.objects.get(entrez_id=entrezid)
                matches.append({'symbol': gene.symbol_hugo, 'species': 'Human', 'entrez_id': entrezid})
                exists.in_genage = True
                exists.save()
            except Gene.DoesNotExist:
                pass

        for gene in modelgenes:
            entrezid = gene.entrez_id
            try:
                exists = Gene.objects.get(entrez_id=entrezid)
                matches.append({'symbol': gene.symbol, 'species': exists.organism.common_name, 'entrez_id': entrezid})
                exists.in_genage = True
                exists.save()
            except Gene.DoesNotExist:
                pass
        
        return render_to_response('admin/check_genage.html', {
            'title': 'GenAge genes in the Digital Ageing Atlas',
            'app_label': 'gene',
            'matches': matches
        }, context_instance=RequestContext(request))
    
    def lookup(self, request, entrezid):
        #fetch = FetchGene()
        #results = fetch.fetchEntrez(entrezid)
        fetch = FetchDetails()
        results = fetch.fetchDetailsFromEntrez(entrezid)
        return HttpResponse(json.dumps(results))

class ReferenceAdmin(VersionAdmin):#admin.ModelAdmin):

    search_fields = ('title', 'author', 'journal', 'book_title', 'editor', 'pubmed')
    list_display = ('id', 'pubmed', '__unicode__',)
    list_display_links = ('id', 'pubmed', '__unicode__',)

    form = ReferenceAdminForm

    class Media:
        js = ('js/lookup.js',)
    
    def get_urls(self):
        urls = super(ReferenceAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^lookup/(?P<pubmed>\d+)/$', self.admin_site.admin_view(self.lookup))
        )
        return extra_urls + urls
    
    def lookup(self, request, pubmed):
        fetch = FetchReference()
        results = fetch.fetchPubmed(pubmed)
        return HttpResponse(json.dumps(results))

class PropertyAdmin(VersionAdmin):#admin.ModelAdmin):
    list_display = ('name', 'description', 'group')

class RelationshipAdmin(VersionAdmin, MPTTModelAdmin):

    search_fields = ('change__name',)
    raw_id_fields = ('change', 'parent', 'references')

    def get_urls(self):
        urls = super(RelationshipAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^editor/$', self.admin_site.admin_view(self.editor), name='relationship_editor_empty'),
            url(r'^editor/(?P<relationship_id>\d+)/$', self.admin_site.admin_view(self.editor), name='relationship_editor')
        )
        return extra_urls + urls

    def queryset(self, request):
        qs = super(RelationshipAdmin, self).queryset(request)
        if 'editor' in request.path:
            return qs.filter(parent=None)
        return qs

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(reverse("admin:relationship_editor", args=(obj.get_root().id,)))

    def response_change(self, request, obj):
        return HttpResponseRedirect(reverse("admin:relationship_editor", args=(obj.get_root().id,)))

    def changelist_view(self, request, extra_context=None):
        if request.GET.get('t') is not None:
            return super(RelationshipAdmin, self).changelist_view(request, extra_context=extra_context)
        return HttpResponseRedirect(reverse("admin:relationship_editor_empty"))

    def relationship(self, obj):
        url = reverse('admin:relationship_editor', args=(obj.pk,))
        return '<a href="{0}">{1}</a>'.format(url, obj.change)
    relationship.allow_tags = True

    @csrf_protect_m
    def delete_view(self, request, object_id, extra_context=None):
        "The 'delete' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label

        obj = self.get_object(request, unquote(object_id))

        if not self.has_delete_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        using = router.db_for_write(self.model)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (deleted_objects, perms_needed, protected) = get_deleted_objects(
            [obj], opts, request.user, self.admin_site, using)

        if request.POST: # The user has already confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = force_unicode(obj)
            self.log_deletion(request, obj, obj_display)
            self.delete_model(request, obj)

            self.message_user(request, _('The %(name)s "%(obj)s" was deleted successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj_display)})

            if not self.has_change_permission(request, None):
                return HttpResponseRedirect(reverse('admin:index', current_app=self.admin_site.name))
            if obj.get_root().id == obj.id:
                return HttpResponseRedirect(reverse('admin:%s_%s_changelist' %
                                        (opts.app_label, opts.module_name),
                                        current_app=self.admin_site.name))
            else:
                return HttpResponseRedirect(reverse("admin:relationship_editor", args=(obj.get_root().id,)))

        object_name = force_unicode(opts.verbose_name)

        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": object_name}
        else:
            title = _("Are you sure?")

        context = {
            "title": title,
            "object_name": object_name,
            "object": obj,
            "deleted_objects": deleted_objects,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": opts,
            "app_label": app_label,
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.delete_confirmation_template or [
            "admin/%s/%s/delete_confirmation.html" % (app_label, opts.object_name.lower()),
            "admin/%s/delete_confirmation.html" % app_label,
            "admin/delete_confirmation.html"
        ], context, current_app=self.admin_site.name)

    def editor(self, request, relationship_id=None):
        ChangeList = self.get_changelist(request)
        list_display = ['action_checkbox', 'relationship']
        list_display_links = ['relationship']
        cl = ChangeList(request, self.model, list_display, list_display_links, self.list_filter,self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)
        cl.formset = None
        nodes = None
        relationship = None
        
        if relationship_id is not None:
            try:
                relationship = Relationship.objects.get(id=relationship_id)
            except:
                raise
            nodes = relationship.get_root().get_descendants(include_self=True)

        return render(request, 'admin/relationship_editor.html', {
            'cl': cl,
            'app_label': self.opts.app_label, 
            'nodes': nodes,
            'relationship': relationship,
            'title': 'Relationship editor',
        })

class DataPointInline(admin.TabularInline):
    model = DataPoint
    extra = 0

class DatasetAdmin(VersionAdmin):#admin.ModelAdmin):
    inlines = (DataPointInline,)

class DataAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__',)
    search_fields = ('change__name', )

admin.site.register(Change, ChangeAdmin)
admin.site.register(Organism)
admin.site.register(Tissue, TissueAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyGroup)
admin.site.register(Person)
admin.site.register(Data, DataAdmin)
admin.site.register(Percentage)
admin.site.register(DataPoint)
admin.site.register(Equation)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(Note)
admin.site.register(Gene, GeneAdmin)
admin.site.register(ProcessMeasured)
