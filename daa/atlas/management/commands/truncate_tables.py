from django.core.management.base import BaseCommand, CommandError

from django.db import connection

class Command(BaseCommand):
    help = 'Truncates database tables for atlas models to allow for clean re-import'

    def handle(self, *args, **options):
        cursor = connection.cursor()

        cursor.execute("truncate atlas_change cascade")
        cursor.execute("truncate atlas_change_people cascade")
        cursor.execute("truncate atlas_change_properties cascade")
        cursor.execute("truncate atlas_change_tissues cascade")
        cursor.execute("truncate atlas_data cascade")
        cursor.execute("truncate atlas_datapoint cascade")
        cursor.execute("truncate atlas_dataset cascade")
        cursor.execute("truncate atlas_equation cascade")
        cursor.execute("truncate atlas_gene cascade")
        cursor.execute("truncate atlas_note cascade")
        cursor.execute("truncate atlas_organism cascade")
        cursor.execute("truncate atlas_percentage cascade")
        cursor.execute("truncate atlas_person cascade")
        cursor.execute("truncate atlas_processmeasured cascade")
        cursor.execute("truncate atlas_property cascade")
        cursor.execute("truncate atlas_propertygroup cascade")
        cursor.execute("truncate atlas_reference cascade")
        cursor.execute("truncate atlas_relationship cascade")
        cursor.execute("truncate atlas_relationship_references cascade")
        cursor.execute("truncate atlas_tissue cascade")
        
