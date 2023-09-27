import json

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import escape, escapejs
from django.conf.urls import *
from django import forms

from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.core import management

from daa.atlas.admin_widgets import ReferenceLookupWidget
from daa.fetchscript.fetch import FetchGene, FetchReference
#from daa.atlas.admin_forms import ReferenceAdminForm
from daa.django_libage.models import BibliographicEntry, Citation, Tag, Source

@receiver(post_delete)
def delete_citation(sender, instance, using, **kwargs):
    if sender.__name__ in ['Name', 'Longevity', 'Gene', 'Variant', 'VariantGroup', 'Change']:
        if using == 'genage_human':
            identifier = unicode(instance.pk).zfill(4)
        elif using == 'default':
            identifier = instance.identifier
            using = 'daa'
        else:
            identifier = instance.pk
        try:
            citation = Citation.objects.get(identifier=identifier, source__short_name=using) 
            citation.delete()
        except:
            pass

class RefCiteInline(admin.TabularInline):
    model = BibliographicEntry.citations.through
    extra = 0

    verbose_name = 'reference'
    verbose_name_plural = 'references'

    raw_id_fields = ('bibliographicentry',)

class CitationAdmin(admin.ModelAdmin):
    search_fields = ('identifier', 'title',)
    list_display = ('identifier', 'title', 'source',)
    list_filter = ('source',)

    inlines = (RefCiteInline,)

    def response_add(self, request, obj, post_url_continue=None):
        if request.GET.get('_popup'):
            opts = obj._meta
            pk_value = obj._get_pk_val()
            refs = []
            for r in obj.bibliographicentry_set.all():
                refs.append(u'<li>{0}</li>'.format(r.formatted_reference()))
            return HttpResponse(
            u'<!DOCTYPE html><html><head><title></title></head><body>'
            u'<script type="text/javascript">opener.dismissLibageReferencePopup(window, "%s", "%s");</script></body></html>' %  (escape(pk_value), escapejs("".join(refs))))
        return super(CitationAdmin, self).response_add(request, obj)

    def response_change(self, request, obj, post_url_continue=None):
        if request.GET.get('_popup'):
            opts = obj._meta
            pk_value = obj._get_pk_val()
            refs = []
            for r in obj.bibliographicentry_set.all():
                refs.append(u'<li>{0}</li>'.format(r.formatted_reference()))
            return HttpResponse(
            u'<!DOCTYPE html><html><head><title></title></head><body>'
            u'<script type="text/javascript">opener.dismissLibageReferencePopup(window, "%s", "%s");</script></body></html>' %  (escape(pk_value), escapejs("".join(refs))))
        return super(CitationAdmin, self).response_change(request, obj)

class TagInline(admin.TabularInline):
    model = BibliographicEntry.tags.through
    extra = 0

    verbose_name = 'tag'
    verbose_name_plural = 'tags'

    raw_id_fields = ('tag',)

class LibAgeReferenceAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'pubmed': ReferenceLookupWidget,
        }

    def clean_pubmed(self):
        return self.cleaned_data['pubmed'] or None 

class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ('citations__identifier', 'pubmed', 'isbn', 'title', 'author','editor', 'publisher', 'year')
    exclude = ('citations', 'tags',)

    inlines = (TagInline,)

    form = LibAgeReferenceAdminForm

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

admin.site.register(BibliographicEntry, ReferenceAdmin)
admin.site.register(Citation, CitationAdmin)
admin.site.register(Tag)
admin.site.register(Source)
