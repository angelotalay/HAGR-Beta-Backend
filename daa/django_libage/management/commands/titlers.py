from django.core.exceptions import ObjectDoesNotExist

from daa.longevity.models import Variant
from daa.genage_human.models import Name
from daa.genage_model.models import Longevity
from daa.gendr.models import Gene
from daa.atlas.models import Change

class Longevity_titler:
    def title(self, identifier):
        missing = []
        try:
            if identifier.startswith('G'):
                vr = Variant.objects.filter(variantgroup=identifier[1:])
                if len(vr) == 0:
                    raise ObjectDoesNotExist
                sig = vr[0].association
                group = 'group'
                genes = list(set([vi.gene.symbol for vi in vr if vi.gene is not None]))
                if len(genes) > 1:
                    loc = 'in {} genes'.format(len(genes))
                elif len(genes) == 1:
                    loc = genes[0]
                else:
                    loc = vr[0].location 
                population = vr[0].population
            else:
                vr = Variant.objects.get(pk=identifier)
                sig = vr.association
                group = 'variant'
                if vr.gene is not None:
                    loc = vr.gene.symbol
                else:
                    loc = vr.location 
                population = vr.population
            title = u"{sig} longevity {group} {loc} for tested {pop} population".format(sig=sig, group=group, loc=loc, pop=population)
        except ObjectDoesNotExist:
            title = None
        return title 

    def check(self, identifier):
        try:
            if identifier.startswith('G'):
                vr = Variant.objects.filter(variantgroup=identifier[1:])
                if len(vr) == 0:
                    raise ObjectDoesNotExist
            else:
                vr = Variant.objects.get(pk=identifier)
        except ObjectDoesNotExist:
            return False
        else:
            return True

class Genage_human_titler:
    def title(self, identifier):
        try:
            nm = Name.objects.get(pk=identifier)
            title = u'{symbol}, {name}'.format(symbol=nm.symbol_hugo, name=nm.name_common)
        except ObjectDoesNotExist:
            title = None
        return title

    def check(self, identifier):
        try:
            nm = Name.objects.get(pk=identifier)
        except ObjectDoesNotExist:
            return False
        return True

class Genage_model_titler:
    def title(self, identifier):
        try:
            ln = Longevity.objects.get(pk=identifier)
            if ln.gene.name != '':
                name = u', {}'.format(ln.gene.name)
            else:
                name = u''
            title = u'{symbol}{name} ({species})'.format(symbol=ln.gene.symbol, name=name, species=ln.gene.organism)
        except ObjectDoesNotExist:
            title = None
        return title

    def check(self, identifier):
        try:
            ln = Longevity.objects.get(pk=identifier)
        except ObjectDoesNotExist:
            return False
        return True

class Gendr_titler:
    def title(self, identifier):
        try:
            gn = Gene.objects.get(pk=identifier)
            if gn.gene_name != '':
                name = u', {}'.format(gn.gene_name)
            else:
                name = u''
            title = u'{symbol}{name} ({species})'.format(symbol=gn.gene_symbol, name=name, species=gn.species_name)
        except ObjectDoesNotExist:
            title = None
        return title

    def check(self, identifier):
        try:
            gn = Gene.objects.get(pk=identifier)
        except ObjectDoesNotExist:
            return False
        return True

class Daa_titler:
    def title(self, identifier):
        try:
            ch = Change.objects.get(identifier=identifier)
            title = u'{name}'.format(name=ch.name)
        except ObjectDoesNotExist:
            title = None
        return title

    def check(self, identifier):
        try:
            ch = Change.objects.get(identifier=identifier)
        except ObjectDoesNotExist:
            return False
        return True
