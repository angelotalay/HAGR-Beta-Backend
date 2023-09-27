from django.core.management.base import BaseCommand, CommandError

from daa.django_libage.models import Citation

import titlers

class Command(BaseCommand):
    args = '<database>'
    help = 'Iterates through each citation in the LibAge database and ensures it has the correct title'

    def handle(self, *args, **options):
        if args[0] == 'all':
            citations = Citation.objects.all()
        else:
            citations = Citation.objects.filter(source__short_name=args[0])

        for c in citations:
            try:
                titleFunc = getattr(titlers, c.source.short_name)
                new_title = titleFunc(c.identifier)
                if new_title is not None:
                    print 'OLD:', c.title
                    print 'NEW:', new_title
                    c.title = new_title
                    c.save()
            except AttributeError:
                pass
