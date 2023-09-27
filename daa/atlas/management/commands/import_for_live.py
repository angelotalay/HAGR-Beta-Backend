from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from daa.atlas.models import *

class Command(BaseCommand):
    args = '<file>'
    help = 'Import data file from a live version export'

    def handle(self, *args, **options):
        with open(args[0], 'r') as f:
            for obj in serializers.deserialize('json', f):
                obj.save()
