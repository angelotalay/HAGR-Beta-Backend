import re

import django_filters

from daa.atlas.models import Tissue, Gene, Reference, Change 

class TissueFilterSet(django_filters.FilterSet):
    number_of_changes = django_filters.NumberFilter()
    class Meta:
        model = Tissue
        fields = ['name', 'synonyms', 'number_of_changes']

    def __init__(self, *args, **kwargs):
        super(TissueFilterSet, self).__init__(*args, **kwargs)
        qd = args[0].lists()
        for k,v in qd:
            if k.startswith('lookups'):
                fn = re.search('lookups\[(.*?)\]', k) 
                self.filters[fn.group(1)].lookup_type = v[0]

class GeneFilterSet(django_filters.FilterSet):
    number_of_changes = django_filters.NumberFilter()
    class Meta:
        model = Gene
        fields = ['name', 'symbol', 'alias', 'omim', 'ensembl', 'uniprot', 'unigene', 'number_of_changes', 'in_genage']

    def __init__(self, *args, **kwargs):
        super(GeneFilterSet, self).__init__(*args, **kwargs)
        qd = args[0].lists()
        for k,v in qd:
            if k.startswith('lookups'):
                fn = re.search('lookups\[(.*?)\]', k) 
                self.filters[fn.group(1)].lookup_type = v[0]

class ReferenceFilterSet(django_filters.FilterSet):
    number_of_changes = django_filters.NumberFilter()
    class Meta:
        model = Reference
        fields = ['title', 'author', 'year', 'number_of_changes']

    def __init__(self, *args, **kwargs):
        super(ReferenceFilterSet, self).__init__(*args, **kwargs)
        qd = args[0].lists()
        for k,v in qd:
            if k.startswith('lookups'):
                fn = re.search('lookups\[(.*?)\]', k) 
                self.filters[fn.group(1)].lookup_type = v[0]

class ChangeFilterSet(django_filters.FilterSet):
    class Meta:
        model = Change
        fields = ['name', 'type', 'gender', 'starts_age', 'ends_age', 'properties', 'properties__group', 'tissues', 'gene__symbol', 'gene__name', 'data__percentage_change', 'data__p_value', 'data__method_collection', 'process_measured', 'organism', 'gene__in_genage']

    def __init__(self, *args, **kwargs):
        super(ChangeFilterSet, self).__init__(*args, **kwargs)
        qd = args[0].lists()
        for k,v in qd:
            if k.startswith('lookups'):
                fn = re.search('lookups\[(.*?)\]', k) 
                self.filters[fn.group(1)].lookup_type = v[0]
