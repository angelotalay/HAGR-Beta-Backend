import json
import csv
import StringIO

from django.contrib import admin
from django.conf.urls import *
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from reversion.admin import VersionAdmin

from daa.cellage.models import CellAgeGo, CellAgeGene, CellAgeBiblio, CellAgeRef, CellAgeMethod, CellAgeSenescence, CellAgeCell, CellAgeCellLine, CellAgeGeneInterventions, CellAgeInterventionCell, CellAgeInterventionCellLine, CellAgeInterventionMethod, CellAgeInterventionSenescence

from daa.fetchscript.fetch import FetchReference, FetchDetails
from daa.django_libage.models import BibliographicEntry, Citation, Source
#
# CellAge
#

class CellAgeGoInline(admin.TabularInline):
    model = CellAgeGo
    extra = 1
    max_num = 250
    verbose_name = 'GO Term'
    verbose_name_plural = 'GO Terms'

class CellAgeInterventionMethodInline(admin.TabularInline):
    model = CellAgeInterventionMethod
    extra = 1
    max_num = 5
    verbose_name = 'Gene Intervention Method'
    verbose_name_plural = 'Gene Intervention Methods'

class CellAgeInterventionCellInline(admin.TabularInline):
    model = CellAgeInterventionCell
    extra = 1
    max_num = 20
    verbose_name = 'Gene Intervention Cell Type'
    verbose_name_plural = 'Gene Intervention Cell Types'

class CellAgeInterventionCellLineInline(admin.TabularInline):
    model = CellAgeInterventionCellLine
    extra = 1
    max_num = 20
    verbose_name = 'Gene Intervention Cell Line Name'
    verbose_name_plural = 'Gene Intervention Cell Line Names'

class CellAgeInterventionSenescenceInline(admin.TabularInline):
    model = CellAgeInterventionSenescence
    extra = 1
    max_num = 3
    verbose_name = 'Gene Intervention Cell Senescence Type'
    verbose_name_plural = 'Gene Intervention Senescence Types'

class CellAgeBiblioAdmin(VersionAdmin):

    search_fields = ('pubmed_id', 'title', 'author', 'journal', 'publisher', 'editor')

    actions = ['bulk_update_references']

    def bulk_update_references(self, request, queryset):
        updated = 0
        total = 0
        for obj in queryset:
            total += 1
            if obj.pubmed_id != '':
                fetch = FetchReference()
                results = fetch.fetchPubmed(obj.pubmed_id)
                for item in results:
                    if (item == 'authors'):
                        authors = ''
                        for i in results[item]:
                            authors += i['last_name'] + ' ' + i['initials'] +', '  
                        obj.__dict__[item] = authors.strip(',')
                    else:
                        obj.__dict__[item] = results[item]
                obj.save()
                updated += 1
        self.message_user(request, '{0} of {1} references where updated'.format(str(updated), str(total)))
    bulk_update_references.short_description = 'Get and update/fill in multiple reference details'

class CellAgeMethodAdmin(VersionAdmin):

    search_fields = ('method',)
    list_display = ('method',)

class CellAgeSenescenceAdmin(VersionAdmin):

    search_fields = ('senescence_type',)
    list_display = ('senescence_type',)

class CellAgeCellAdmin(VersionAdmin):

    search_fields = ('cell_type',)
    list_display = ('cell_type',)

class CellAgeCellLineAdmin(VersionAdmin):

    search_fields = ('cell_line_name',)
    list_display = ('cell_line_name',)

class CellAgeGeneAdmin(VersionAdmin):

    search_fields = ('entrez_id','gene_name','description',)
    list_display = ('entrez_id','gene_name','description',)

    inlines = [CellAgeGoInline]

    actions = ['bulk_update_go_terms']

    def bulk_update_go_terms(self, request, queryset):
        updated = 0
        total = 0
        for obj in queryset:
            total += 1
            if obj.entrez_id != '':

                f = FetchDetails()
                entrezd = f.fetchDetailsFromEntrez(obj.entrez_id)
                results = dict(entrezd.items())
                
                CellAgeGo.objects.filter(entrez_id=obj.entrez_id).delete()

                for item in results:
                    if (item == 'go'):
                        for t in results[item]:
                            go_type = None
                            if t['type'] == 'Process':
                                go_type = 'P'
                            elif t['type'] == 'Component':
                                go_type = 'C'
                            elif t['type'] == 'Function':
                                go_type = 'F'

                            gene_pk = CellAgeGene.objects.get(pk=obj.entrez_id)
                            cellagenew = CellAgeGo(entrez_id=gene_pk, go=t['go'], name=t['name'], go_type=go_type)
                            cellagenew.save()
                            updated += 1
        self.message_user(request, '{0} GO terms added across {1} genes'.format(str(updated), str(total)))
    bulk_update_go_terms.short_description = 'Refresh GO data'

class CellAgeGeneInterventionsAdmin(VersionAdmin):

    search_fields = ('hagr_id','gene_name','hgnc_id','entrez_id','organism','cancer_type','senescence_effect','description','notes')
    list_display = ('hagr_id','gene_name','entrez_id','senescence_effect','cancer_type')

    inlines = [CellAgeInterventionSenescenceInline, CellAgeInterventionCellInline, CellAgeInterventionCellLineInline, CellAgeInterventionMethodInline]

    def get_urls(self):
        urls = super(CellAgeGeneInterventionsAdmin, self).get_urls()
        extra_urls = patterns('',
            url(r'^clear_libage/$', self.admin_site.admin_view(self.clearlibage), name='cellage_clearlibage'),
            url(r'^import/$', self.admin_site.admin_view(self.csvimport), name='cellage_csvimport'),
            url(r'^export/$', self.admin_site.admin_view(self.export), name='cellage_csvexport'),
            url(r'^import/item/(?P<rid>\d+)/$', self.admin_site.admin_view(self.csvimportitem), name='cellage_csvimportitem'),
        )
        return extra_urls + urls

    def clearlibage(self, request):
        citations = Citation.objects.filter(source__short_name='cellage')
        citations.delete()
        return render(request, 'libage_deleted.html', {'title': 'Delete CellAge citations from LibAge', 'app_label': 'CellAge'})

    def export(self, request):
        from django.db import connections
        cursor = connections['cellage'].cursor()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=cellage.csv'
        response['Content-Encoding'] = 'UTF-8'
        response['Content-type'] = 'text/csv; charset=UTF-8'

        cursor.execute("""SELECT i.gene_name, i.hgnc_id, GROUP_CONCAT(DISTINCT m.method SEPARATOR ';'), i.entrez_id, i.organism, GROUP_CONCAT(DISTINCT c.cell_type SEPARATOR ';'), GROUP_CONCAT(DISTINCT l.cell_line_name SEPARATOR ';'), i.cancer_type, senescence_effect, GROUP_CONCAT(DISTINCT s.senescence_type SEPARATOR ';'), GROUP_CONCAT(DISTINCT b.pubmed_id SEPARATOR ';'), i.description, i.notes 
                        FROM gene_interventions i, intervention_method m, intervention_cell c, intervention_cell_line l, intervention_senescence s, ref r, biblio b
                        WHERE i.hagr_id = m.hagr_id
                          AND i.hagr_id = c.hagr_id
                          AND i.hagr_id = s.hagr_id 
                          AND i.hagr_id = r.hagr_id
                          AND i.hagr_id = l.hagr_id
                          AND r.pubmed_id = b.pubmed_id
                    GROUP BY i.gene_name, i.hgnc_id, i.entrez_id, i.organism, i.cancer_type, i.description, i.notes""")

        drugs = cursor.fetchall()
        writer = csv.writer(response)

        writer.writerow(['gene_name','hgnc_id','method', 'entrez_id','organism','cell_type','cell_line','cancer_type','senescence_effect','senescence_type','pubmed_id','description','notes'])
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
            return render(request, 'import_complete.html', {'title': 'Import complete', 'app_label': 'CellAgeGeneInterventions', 'data': json.dumps(output)})
        return render(request, 'import_cellage.html', {'title': 'Import into CellAge', 'app_label': 'CellAgeGeneInterventions'})

    @csrf_exempt
    def csvimportitem(self, request, rid):
        r = request.POST
        if r:
            print r
            print rid

            entrez_id = int(r['entrez_id'].strip())

            f = FetchDetails()
            g = f.fetchDetailsFromEntrez(entrez_id)
                  
            try:  
                gene_symbol = g['symbol']
                gene_name = g['name']
                description = g['description']
                chr_loc = g['chromosome_location']
                chr_start = g['location_start'] 
                chr_end = g['location_end']
                orientation = g['orientation']
                accession = g['accession'] 
                unigene = g['unigene']
                omim = g['omim'] 
                ensembl = g['ensembl'] 
                hprd = g['hprd'] 
                species = g['species']
                alias = g['alias']
                homologene = g['homologene']
                go_terms = g['go']
            except Exception as e: 
                raise Exception("Failed obtaining gene data from NCBI. Encountered the following: " + str(e)) 
  
            try:
                gene = CellAgeGene(entrez_id = entrez_id, gene_symbol=gene_symbol, gene_name=gene_name, description=description, chr_loc=chr_loc, chr_start=chr_start, chr_end=chr_end, orientation=orientation, accession=accession, unigene=unigene, omim=omim, ensembl=ensembl, hprd=hprd, species=species, alias=alias, homologene=homologene)
                gene.save()
                gene_pk = CellAgeGene.objects.get(pk=gene.pk)
            except Exception as e:
                msg = "Entrez_id: " + str(entrez_id)
                msg += "\n Gene Name: " + gene_name
                msg += "\n Gene Symbol: " + gene_symbol

                raise Exception(" Encountered the following error during insert: " + str(e) + '. For the following gene: ' + msg)

            try:
                for t in go_terms:
                    go_type = None
                    if t['type'] == 'Process':
                        go_type = 'P'
                    elif t['type'] == 'Component':
                        go_type = 'C'
                    elif t['type'] == 'Function':
                        go_type = 'F'

                    go = CellAgeGo(entrez_id = gene_pk, go = t['go'], name = t['name'], go_type = go_type)
                    go.save()
            except Exception as e:
                raise Exception('Failed to insert GO data for Entrez Id:' + str(entrez_id) + '.\n The Following error was encountered: ' +  str(e))

            gene_name = r['gene_name'].strip()
            hgnc_id = r['hgnc_id'].strip()
            entrez_id = r['entrez_id'].strip()
            organism = r['organism'].strip()
            cancer_type = r['cancer_type'].strip()
            effect = r['senescence_effect'].strip()
            description = r['description'].strip()
            notes = r['notes'].strip()

            intervention = CellAgeGeneInterventions(gene_name=gene_name, hgnc_id=hgnc_id, entrez_id=entrez_id, organism=organism, cancer_type=cancer_type, senescence_effect=effect, description=description, notes=notes)
            intervention.save()
            intervention_pk = CellAgeGeneInterventions.objects.get(pk=intervention.pk)

            methods = r['method'].split(';')
            cell_types = r['cell_type'].split(';')
            senescence_types = r['senescence_type'].split(';')
            cell_lines = r['cell_line'].split(';')

            for method in methods:
                method = method.strip()
                method_pk = CellAgeMethod.objects.get(pk=method)
                CellAgeInterventionMethod.objects.create(hagr_id = intervention_pk, method = method_pk)

            for cell_type in cell_types:
                cell_type = cell_type.strip()
                cell_type_pk = CellAgeCell.objects.get(pk=cell_type)
                CellAgeInterventionCell.objects.create(hagr_id = intervention_pk, cell_type = cell_type_pk)

            for senescence_type in senescence_types:
                senescence_type = senescence_type.strip()
                senescence_type_pk = CellAgeSenescence.objects.get(pk=senescence_type)
                CellAgeInterventionSenescence.objects.create(hagr_id = intervention_pk, senescence_type = senescence_type_pk)

            for cell_line_name in cell_lines:
                cell_line_name = cell_line_name.strip()
                cell_line_pk = CellAgeCellLine.objects.get(pk=cell_line_name)
                CellAgeInterventionCellLine.objects.create(hagr_id = intervention_pk, cell_line_name = cell_line_pk)

            pubmed_ids = r['pubmed'].split(';')

            for pubmed_id in pubmed_ids:

                pubmed_id = int(pubmed_id)

                try:
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
                except Exception as e:
                    raise Exception("Error obtaining biblio data from NCBI for PubMed Id: " + str(pubmed_id))

                try:
                    biblio = CellAgeBiblio(pubmed_id=pubmed_id, terms=terms, title=title, journal = journal, author = author, volume = volume, authors = authors, year=year, author_initials = author_initials, contact_addresses = contact_addresses, issue = issue, pages = pages, editor = editor, review = review, publisher = publisher, url = url)

                    biblio.save()
                    biblio_pk = CellAgeBiblio.objects.get(pk=biblio.pk)
                except Exception as e:
                    raise Exception("Error saving biblio data to database for PubMed Id: " + str(pubmed_id) + ". Encountered the following: " + str(e))
         
                try:
                    ref = CellAgeRef(hagr_id = intervention_pk, pubmed_id = biblio_pk)
                    ref.save()
                    ref_pk = CellAgeRef.objects.latest('ref_id')
                except Exception as e:
                    raise Exception("Error saving new HAGR reference for PubMed Id: " + str(pubmed_id) + ". Encountered the following: " + str(e) )

                try:
                    title = u'{gene_name} {effect} cell senescence.'.format(gene_name=unicode(r['gene_name']), effect=unicode(r['senescence_effect']))
                    source = Source.objects.get(short_name='cellage')
                    cited = Citation(identifier=ref_pk, title=title, source=source)
                    cited.save()

                    ref = BibliographicEntry.objects.get_or_create_from_pubmed(pubmed_id)
                    ref.citations.add(cited)
                except Exception as e:
                    raise Exception("Error created new citation entry for PubMed Id: " + str(pubmed_id) + ". The following error was encountered: " + str(e))

            return HttpResponse('Complete', content_type="text/plain")

admin.site.register(CellAgeBiblio, CellAgeBiblioAdmin)
admin.site.register(CellAgeGeneInterventions, CellAgeGeneInterventionsAdmin)
admin.site.register(CellAgeMethod, CellAgeMethodAdmin)
admin.site.register(CellAgeSenescence, CellAgeSenescenceAdmin)
admin.site.register(CellAgeCell, CellAgeCellAdmin)
admin.site.register(CellAgeCellLine, CellAgeCellLineAdmin)
admin.site.register(CellAgeInterventionCell)
admin.site.register(CellAgeInterventionCellLine)
admin.site.register(CellAgeInterventionMethod)
admin.site.register(CellAgeInterventionSenescence)
admin.site.register(CellAgeGene, CellAgeGeneAdmin)
