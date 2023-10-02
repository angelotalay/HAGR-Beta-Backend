import csv
import re

from django.core.management.base import BaseCommand, CommandError

from daa.genage_human.models import Name, Go 
from daa.django_libage.models import Citation

class Command(BaseCommand):
    help = 'Get all pubmeds for each entry to allow search'

    def handle(self, *args, **options):
        all_entries = Name.objects.all()

        for entry in all_entries:
            citation = Citation.objects.get(identifier=str(entry.id_hagr).zfill(4), source__short_name='genage_human')
            pubmeds = []
            for b in citation.bibliographicentry_set.all():
                pubmeds.append(b.pubmed)

            entry.pubmed = ",".join([p for p in pubmeds if p is not None])
            entry.save()
