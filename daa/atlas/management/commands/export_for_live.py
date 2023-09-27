from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from daa.atlas.models import * 

class Command(BaseCommand):
    help = 'Exports data for import into the live version'

    def handle(self, *args, **options):

        organisms = Organism.objects.all()
        people = Person.objects.all()
        processes_measured = ProcessMeasured.objects.all()
        tissues = Tissue.objects.all()
        genes = Gene.objects.filter(change__hide=False)
        property_groups = PropertyGroup.objects.all()
        properties = Property.objects.all()

        data_model = Data.objects.all()
        data_point = DataPoint.objects.all()
        equations = Equation.objects.all()
        percentages = Percentage.objects.all()
        dataset = Dataset.objects.all()

        changes = Change.objects.filter(hide=False)

        relationships = Relationship.objects.all()

        exported_relationships = []
        hide = []
        for r in relationships:
            if r.change.hide == True:
                hide.extend(list(r.get_descendants(include_self=True)))
            else:
                if r not in hide:
                    exported_relationships.append(r)
            '''
            if r.change.hide != False and r.id not in hide and r.parent_id not in hide :
                exported_relationships.append(r)
            if r.change.hide == True:
                print r.change.id
                hide.append(r.id)
            '''

        combined = list(organisms) + list(people) + list(processes_measured) + list(tissues) + list(genes) + list(property_groups) + list(properties) + list(data_model) + list(data_point) + list(equations) + list(percentages) + list(dataset) + list(changes) + list(exported_relationships)
        
        data = serializers.serialize('json', combined, indent=4)

        self.stdout.write(data)
