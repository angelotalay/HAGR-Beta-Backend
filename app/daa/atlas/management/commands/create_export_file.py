# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from daa.atlas.models import * 
from daa.django_libage.models import *

class Command(BaseCommand):
    help = 'Exports data for import into the live version'

    def handle(self, *args, **options):
        export_header = ['Identifier','Change name','Change type', 'Species', 'Change gender', 'Age change starts', 'Age change ends', 'Description', 'Tissues', 'Gene', 'Properties', 'Type of data', 'Process measured', 'Sample size', 'Method of collection', 'Data transforms', 'Percentage change', 'P value', 'Coefficiant', 'Intercept', 'Relationship parent identifiers', 'References (with LibAge reference ID in brackets)']
        self.stdout.write(unicode(u"\t".join(export_header)+u"\n").encode('utf-8'))

        qs = Change.objects.exclude(type='Pathological')

        for e in qs:
            tissues = u", ".join([t.name.title() for t in e.tissues.all()])
            gene = e.gene.compound_name() if e.gene is not None else u""
            properties = u", ".join([prp.name for prp in e.properties.all()])
            process_measured = e.process_measured.name if e.process_measured is not None else u''
            
            relationship_child = u''
            relationship_parent = u''
            relationship = Relationship.objects.filter(change=e.id) 
            if relationship.count() > 0:
                rp = []
                rc = []
                for r in relationship:
                    if r.parent is not None:
                        rp.append(r.parent.change.identifier)
                relationship_parent = u",".join(rp)

            refs = BibliographicEntry.objects.filter(citations__identifier=e.identifier, citations__source__short_name='daa')
            refset = []
            for r in refs:
                refset.append(r.reference())
            references = "|".join(refset)

            try:
                d = e.data
                if d is not None:
                    data = {
                        u'type': d.type,
                        u'sample_size': d.sample_size,
                        u'method_collection': d.method_collection,
                        u'data_transforms': d.data_transforms,
                        u'percentage_change': d.percentage_change,
                        u'p_value': d.p_value,
                    }
                    try:
                        eq = d.data.equation
                        equation = {
                            u'coefficiant': eq.coefficiant,
                            u'intercept': eq.intercept,
                        }
                    except:
                        equation = {}
                    data.update(equation)
                else:
                    data = {}
            except ObjectDoesNotExist:
                data = {}

            tmp = u"{id}\t{name}\t{type}\t{species}\t{gender}\t{start}\t{end}\t{description}\t{tissues}\t{gene}\t{properties}\t{dtype}\t{measure}\t{dsample}\t{dmethod}\t{dtransforms}\t{dpercent}\t{dpvalue}\t{dcoefficiant}\t{dintercept}\t{relationship_parent}\t{references}\n".format(id=e.identifier, name=e.name, type=e.type, gender=e.gender, start=e.starts_age, end=e.ends_age, description=e.description, tissues=tissues, gene=gene, properties=properties, dtype=data.get('type', u''), measure=process_measured, dsample=data.get('sample_size', u''), dmethod=data.get('method_collection', u''), dtransforms=data.get('data_transforms', u''), dpercent=data.get('percentage_change', u''), dpvalue=data.get('p_value', u''), dcoefficiant=data.get('coefficiant', u''), dintercept=data.get('intercept', u''), species=e.organism.name, relationship_parent=relationship_parent, references=references)

            if len(refset) > 0:
                self.stdout.write(unicode(tmp).encode('utf-8'))
