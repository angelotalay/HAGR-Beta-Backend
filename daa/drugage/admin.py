import json
import csv
import StringIO

from django.db import IntegrityError
from django.contrib import admin
from django.conf.urls import *
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.db.models import Q, Count
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from mptt.admin import MPTTModelAdmin

from reversion.admin import VersionAdmin

from daa.drugage.models import DrugAgeResults, DrugAgeBiblio, DrugAgeCompounds, DrugAgeCompoundSynonyms
from daa.django_libage.models import BibliographicEntry, Citation, Tag, Source
from daa.atlas.admin_widgets import SelectableForeignKeyRawIdWidget, EditForeignKeyRawIdWidget, GeneLookupWidget, ReferenceLookupWidget 
from daa.atlas.fetch import FetchGene, FetchReference, FetchDetails
from daa.atlas.admin_forms import ReferenceAdminForm


#
# DrugAge
#

class DrugAgeCompoundsAdmin(admin.ModelAdmin):
    list_display = ('id','compound_name','cas_number','pubchem_cid','iupac_name')
    search_fields = ('compound_name', 'cas_number', 'pubchem_cid', 'iupac_name')

class DrugAgeCompoundSynonymsAdmin(admin.ModelAdmin):
    list_display = ('id','compound_id','synonym')
    search_fields = ('compound_id__compound_name', 'synonym')

class DrugAgeBiblioAdmin(admin.ModelAdmin):

    search_fields = ('title', 'author', 'journal', 'publisher', 'editor', 'pubmed')

class DrugAgeResultsAdmin(admin.ModelAdmin):
    list_display = ('id', 'compound_id', 'species', 'strain', 'avg_lifespan_change_percent', 'max_lifespan_change_percent','dosage','gender','pubmed_id','notes','last_modified')
    list_display_links = ('id','compound_id')
    ordering = ('-last_modified',)
 
    search_fields = ('compound_id__compound_name', 'species', 'strain', 'avg_lifespan_change_percent', 'max_lifespan_change_percent','dosage','gender','pubmed_id','notes')

    def get_urls(self):
        urls = super(DrugAgeResultsAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^import/$', self.admin_site.admin_view(self.csvimport), name='drugage_csvimport'),
            url(r'^export/$', self.admin_site.admin_view(self.export), name='drugage_csvexport'),
            url(r'^import/item/(?P<rid>\d+)/$', self.admin_site.admin_view(self.csvimportitem), name='drugage_csvimportitem'),
        )
        return extra_urls + urls

    def export(self, request):
        from django.db import connections
        cursor = connections['drugage'].cursor()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=drugage_entries.csv'
        response['Content-Encoding'] = 'UTF-8'
        response['Content-type'] = 'text/csv; charset=UTF-8'

        cursor.execute("SELECT c.compound_name, c.cas_number, r.species, r.strain, r.dosage, r.avg_lifespan_change_percent, r.max_lifespan_change_percent, r.gender, r.significance, b.pubmed, r.notes, r.last_modified FROM results r, compounds c, biblio b WHERE r.compound_id = c.id AND r.biblio_id = b.id_biblio")

        drugs = cursor.fetchall()
        writer = csv.writer(response, dialect='excel')

        writer.writerow(['compound_name','cas_number','species', 'strain','dosage','avg_lifespan_change','max_lifespan_change','gender','significance','pubmed_id','notes','last_modified'])
        for row in drugs:
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
                output = []
                for rid, r in enumerate(csv.DictReader(StringIO.StringIO(chunk), delimiter=",")):
                    output.append({'rid': rid, 'data': r})
            return render(request, 'admin/import_drugage_complete.html', {'title': 'Import complete', 'app_label': 'DrugAgeResults', 'data': json.dumps
(output)})
        return render(request, 'admin/import_drugage.html', {'title': 'Import DrugAge', 'app_label': 'DrugAgeResults'})

    @csrf_exempt
    def csvimportitem(self, request, rid):
        r = request.POST
        if r:
            print r
            print rid

            pubmed_id = r['pubmed_id']

            fetch = FetchReference()
            p = fetch.fetchPubmed(pubmed_id, True)

            terms = p['terms']
            title = p['title'].encode('utf-8')
            journal = p['journal']
            author = p['author']
            volume = p['volume']
            authors = ''
            year = p['year']
            author_initials = p['author_initials']
            contact_addresses = ''
            issue = p['issue']
            pages = p['pages']
            editor = ''
            review = '' #p['review']
            publisher = ''
            url = ''

            biblio, created = DrugAgeBiblio.objects.get_or_create(pubmed = pubmed_id)
            biblio.terms = terms 
            biblio.title = title 
            biblio.journal = journal
            biblio.author = author
            biblio.volume = volume
            biblio.authors = authors 
            biblio.author_initials = author_initials 
            biblio.year = year 
            biblio.contact_addresses = contact_addresses 
            biblio.issue = issue 
            biblio.pages = pages 
            biblio.editor = editor 
            biblio.review = review 
            biblio.publisher = publisher
            biblio.url = url
            biblio.save()

            compound_name = r['compound_name']
            cas_number = r['cas_number']
            species = r['species']
            strain = r['strain']
            dosage = r['dosage']
            avg_lifespan_change_percent = r['avg_lifespan_change']
            max_lifespan_change_percent = r['max_lifespan_change']
            gender = r['gender']
            significance = r['significance']
            notes = r['notes']

            if avg_lifespan_change_percent == '':
                avg_lifespan_change_percent = None

            if max_lifespan_change_percent == '':
                max_lifespan_change_percent = None
 
            compound, created = DrugAgeCompounds.objects.get_or_create(compound_name=compound_name);           
            compound.cas_number = cas_number
            compound.save

            result = DrugAgeResults.objects.create(compound_id=compound, biblio_id = biblio, species=species, strain=strain, dosage=dosage, avg_lifespan_change_percent=avg_lifespan_change_percent, max_lifespan_change_percent=max_lifespan_change_percent, gender=gender, pubmed_id=pubmed_id,significance=significance, notes=notes)

            result_pk = result.id

            try:
                ref = BibliographicEntry.objects.get_or_create_from_pubmed(pubmed = pubmed_id)
            except IntegrityError as e:
                pass

            lifespan = ''

            if avg_lifespan_change_percent is not None:
                lifespan = 'an avg lifespan change of ' + avg_lifespan_change_percent
            elif max_lifespan_change_percent is not None:
                lifespan = 'a max lifespan change of ' + max_lifespan_change_percent

            if gender is None:
                gender = ''

            title = u"{compound_name} demonstrated {lifespan} in {gender} {species}".format(compound_name=compound_name, lifespan=lifespan, gender=gender, species=species)
            source = Source.objects.get(short_name='drugage')
            cited = Citation(identifier=result_pk, title=title, source=source)
            cited.save()
            ref.citations.add(cited) 

            return HttpResponse('Complete', content_type="text/plain")

admin.site.register(DrugAgeResults, DrugAgeResultsAdmin)
admin.site.register(DrugAgeBiblio, DrugAgeBiblioAdmin)
admin.site.register(DrugAgeCompounds, DrugAgeCompoundsAdmin)
admin.site.register(DrugAgeCompoundSynonyms, DrugAgeCompoundSynonymsAdmin)
