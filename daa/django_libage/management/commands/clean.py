from django.core.management.base import BaseCommand, CommandError

from daa.django_libage.models import Citation

import titlers

class Command(BaseCommand):
    args = '<database>'
    help = 'Iterates through each citation in the LibAge database and ensures that it is correct, removing orphan entries'

    def handle(self, *args, **options):
        if args[0] == 'all':
            citations = Citation.objects.all()
        else:
            citations = Citation.objects.filter(source__short_name=args[0])

        for c in citations:
            try:
                tclass = getattr(titlers, c.source.short_name.capitalize()+'_titler')()
            except AttributeError as e:
                pass
            else:
                if tclass.check(c.identifier):
                    self.retitle(c)
                else:
                    #print 'nep:', c.identifier, c.source
                    self.delete(c)

    def retitle(self, c):
        try:
            tclass = getattr(titlers, c.source.short_name.capitalize()+'_titler')()
            new_title = tclass.title(c.identifier)
            if new_title is not None:
                #print 'OLD:', c.title
                #print 'NEW:', new_title
                c.title = new_title
                c.save()
        except AttributeError:
            pass

    def delete(self, c):
        c.delete()
