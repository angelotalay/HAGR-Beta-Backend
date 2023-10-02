import csv

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from daa.gendr.models import Gene
from daa.django_libage.models import Citation

class Command(BaseCommand):
    help = 'Convert entrez PKs to auto PKs in Libage'

    def handle(self, *args, **options):
        for a in Gene.objects.all():
            try:
                c = Citation.objects.get(identifier=a.entrez_id, source__short_name='gendr')
                c.identifier = str(a.id)
                c.save()
            except ObjectDoesNotExist:
                print a
