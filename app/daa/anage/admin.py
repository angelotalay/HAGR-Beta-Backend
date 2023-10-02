import json
import csv
import StringIO

from django.contrib import admin
from django.conf.urls import *
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.db.models import Q, Count
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers

from mptt.admin import MPTTModelAdmin

from reversion.admin import VersionAdmin

from daa.anage.models import AnageName, AnageBiblio, AnageAge, AnageLinks, AnageMetabolism, AnageRef
from daa.atlas.admin_widgets import SelectableForeignKeyRawIdWidget, EditForeignKeyRawIdWidget, GeneLookupWidget, ReferenceLookupWidget 
from daa.atlas.fetch import FetchGene, FetchReference
from daa.atlas.admin_forms import ReferenceAdminForm

#
# Anage
#

class AnageBiblioAdmin(VersionAdmin):

    search_fields = ('title', 'author', 'journal', 'book_title', 'editor', 'pubmed')

    form = ReferenceAdminForm

    actions = ['bulk_update_references']

    class Media:
        js = ('js/lookup.js',)
    
    def get_urls(self):
        urls = super(AnageBiblioAdmin, self).get_urls()
        extra_urls = patterns('',
            (r'^lookup/(?P<pubmed>\d+)/$', self.admin_site.admin_view(self.lookup))
        )
        return extra_urls + urls
    
    def lookup(self, request, pubmed):
        fetch = FetchReference()
        results = fetch.fetchPubmed(pubmed)
        return HttpResponse(json.dumps(results))

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

class AnageRefInline(admin.TabularInline):
    model = AnageRef
    extra = 0
    verbose_name_plural = 'references'
    verbose_name = 'reference'

    raw_id_fields = ('id_biblio', )
    #template = 'admin/tabular.html'

class AnageLinksInline(admin.StackedInline):
   model = AnageLinks 
   extra = 0
   verbose_name = 'links'
   verbose_name_plural = 'links'

class AnageMetabolismInline(admin.StackedInline):
   model = AnageMetabolism 
   extra = 0
   verbose_name = 'metabolism'
   verbose_name_plural = 'metabolism'

class AnageAgeInline(admin.StackedInline):
   model = AnageAge 
   extra = 0
   verbose_name = 'age'
   verbose_name_plural = 'age'

   raw_id_fields = ('biblioid',)
        
class AnageNameAdmin(VersionAdmin):#admin.ModelAdmin):
    list_display = ('name_common', 'genus', 'species', 'synonyms')
    list_display_links = ('name_common',)
    
    search_fields = ('name_common', 'genus', 'species', 'synonyms',)

    inlines = [AnageLinksInline, AnageMetabolismInline, AnageAgeInline, AnageRefInline]

admin.site.register(AnageName, AnageNameAdmin)
admin.site.register(AnageBiblio, AnageBiblioAdmin)
