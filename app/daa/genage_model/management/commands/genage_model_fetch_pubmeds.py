import csv
import re

from django.core.management.base import BaseCommand, CommandError

from daa.genage_model.models import Model
from daa.django_libage.models import Citation

class Command(BaseCommand):
    help = 'Get all pubmeds for each entry to allow search'

    def handle(self, *args, **options):
        all_entries = Model.objects.all()

        for entry in all_entries:
            pubmeds = []
            for le in entry.longevity_set.all():
                try:
                    citation = Citation.objects.get(identifier=le.id, source__short_name='genage_model')
                    for b in citation.bibliographicentry_set.all():
                        pubmeds.append(b.pubmed)
                except:
                    pass

            entry.pubmed = ",".join([p for p in pubmeds if p is not None])
            entry.save()
