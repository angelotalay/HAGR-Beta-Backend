import re
import json
import datetime

from django.contrib import admin
from django.conf.urls import *
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

from reversion.admin import VersionAdmin

from daa.fetchscript.fetch import FetchDetails

from daa.genage_model.models import Model, Longevity
from daa.gendr.models import Gene as GenDRGene
from daa.longevity.models import Gene, Variant, Population, Variant, VariantGroup
from daa.django_libage.models import BibliographicEntry, Citation, Source, Tag

from daa.submissions.models import Submission

VALID_GENMOD = (
    'lifespan_effect',
    'phenotype_description',
    'longevity_influence',
    'max_lifespan_change',
    'avg_lifespan_change',
    'max_lifespan_change_desc',
    'avg_lifespan_change_desc',
    'method',
    )

VALID_GENDR = (
    'organism',
    'description',
    )

VALID_LONG = (
    'association',
    'population',
    'study_design',
    'conclusions',
    )

class SubmissionAdmin(VersionAdmin):
    list_display = ('date_submitted', 'formatted_submission', 'database', 'submitter_name', 'is_added',)
    actions = ['convert_to_entry', 'mark_complete']

    list_filter = ('is_added', 'database',)

    def formatted_submission(self, obj):
        values = json.loads(obj.submission)
        output = ''
        for k,v in values.iteritems():
            output += u'<b>{}</b>: {}<br>'.format(k,v)
        return output
    formatted_submission.allow_tags = True

    def mark_added(self, obj, user):
        obj.is_added = True
        obj.added_by = user
        obj.added_on = datetime.date.today()
        obj.save()

    def add_citation(self, obj, data, title, identifier):
        source = Source.objects.get(short_name=obj.database)
        be = BibliographicEntry.objects.get_or_create_from_pubmed(data['pubmed'])
        cite = Citation(identifier=identifier, title=title, source=source)
        cite.save()
        be.citations.add(cite)

    def mark_complete(self, request, queryset):
        marked = 0
        for obj in queryset:
            self.mark_added(obj, request.user)
            marked += 1
        self.message_user(request, '{} entries have been marked complete'.format(marked))
    mark_complete.short_description = 'Mark entries as complete (does not add entry)'

    def convert_to_entry(self, request, queryset):
        f = FetchDetails()
        entries_created = 0
        for obj in queryset:
            data = json.loads(obj.submission)

            if re.search(r'[A-Za-z]', data['identifier']) is None:
                entrez = data['identifier']
            else:
                organism = data['organism'] if 'organism' in data else 'human'
                entrez = f.convertToEntrezGeneID(data['identifier'], organism=organism)

            if obj.database == 'genage_model':
                try:
                    entry = Model.objects.get(entrez_id=entrez)
                except Model.DoesNotExist:
                    gene = f.fetchDetailsFromEntrez(entrez)
                    entry = Model(entrez_id=entrez, symbol=gene['symbol']) 

                ld = {k:v for k,v in data.iteritems() if k in VALID_GENMOD}
                l = Longevity(gene=entry, **ld)
                entry.save()

                title = entry.symbol
                self.add_citation(obj, data, title, entry.entrez_id)

                self.mark_added(obj, request.user)
                entries_created += 1

            elif obj.database == 'gendr':
                gene = f.fetchDetailsFromEntrez(entrez)
                print gene, entrez
                entry = GenDRGene(gene_symbol=gene['symbol'], entrez_id=entrez, gene_id=gene['ensembl'], species_name=data['organism'], gene_name=gene['name'], ensembl=gene['ensembl'], description=data['description'])
                entry.save()

                title = entry.gene_symbol
                self.add_citation(obj, data, title, entry.entrez_id)

                self.mark_added(obj, request.user)
                entries_created += 1

        self.message_user(request, '{} entries have been created'.format(entries_created))
    convert_to_entry.short_description = 'Convert submission to database entry'

admin.site.register(Submission, SubmissionAdmin)
