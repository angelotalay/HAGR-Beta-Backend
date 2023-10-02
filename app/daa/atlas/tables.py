from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.core.context_processors import csrf
from django.middleware.csrf import get_token

import django_tables2 as tables
from django_tables2 import A
from django.db.models import Count

from daa.atlas.models import Change, Gene, Tissue, Reference, Percentage, Dataset

class GeneColumn(tables.Column):
    def render(self, value, record):
        try:
            gene = record.gene
            if gene != None:
                return mark_safe('<a href="'+reverse('daa.atlas.views.gene', args=[gene.entrez_id])+'">'+str(gene.symbol)+'</a>') 
            return u'N/A'
        except AttributeError:
            return u'N/A'

class DataColumn(tables.Column):
    def render(self, value, record):
        cell = ''
        if record.data is not None:
            if record.data.percentage_change is not None:
                isneg = False
                if hasattr(record.data, 'percentage'):
                    if record.data.percentage.is_negative:
                        isneg = True
                if hasattr(record.data, 'equation'):
                    if record.data.equation.is_negative:
                        isneg = True
                percentage_change = u"{:.1f}".format(record.data.percentage_change)
                cell = u'<span class="data-change {0}">{1} {2} </span><span class="process-measured">{3}</span>'.format(
                    u'negative' if isneg else u'positive', 
                    percentage_change.lstrip('-')+u'%' if percentage_change != '0.0' else u'',
                    u'Decrease' if isneg else u'Increase',
                    record.process_measured)
            elif record.data.dataset is not None:
                cell = u'<span class="data-series">{0}</span><span class="process-measured">{1}</span>'.format('Series', record.process_measured)
            else:
                return u'N/A'
        else:
            return u'N/A'
        return mark_safe(cell)

class TissueColumn(tables.Column):
    def render(self, value, record):
        tissues = ''
        for t in record.tissues.all():
            tissues += '<a href="'+reverse('daa.atlas.views.tissue', args=[t.evid])+'">'+t.name+'</a>, '
        return mark_safe(tissues.strip(' ,'))

class GeneNameColumn(tables.Column):
    def render(self, value, record):
        return mark_safe('<a href="'+reverse('daa.atlas.views.gene', args=[record.entrez_id])+'"><b>'+record.symbol+'</b>: '+record.name+'</a>')

class TissueStructureColumn(tables.Column):
    def render(self, value, record):
        return ''

class ChangesAssociatedColumn(tables.Column):
    def render(self, value, record):
        return record.change_set.count()

class ReferenceTitleColumn(tables.Column):
    def render(self, value, record):
        if record.book_title != '':
            title = record.book_title
        else:
            title = record.title
        return mark_safe('<a href="'+reverse('daa.atlas.views.reference', args=[record.id])+'">'+title+'</a>')

class ReferenceSourceColumn(tables.Column):
    def render(self, value, record):
        if record.pubmed is not None:
            link = u' (<a href="http://www.ncbi.nlm.nih.gov/pubmed/{0}">Pubmed</a>)'.format(record.pubmed)
        elif record.url is not None:
            link = u' (<a href="{0}">Link</a>)'.format(record.url)
        else:
            link = u''  
        ref_format = u'<i>{0}</i>  <b>{1}</b> {2} {3}'.format(record.journal, record.volume, record.pages, link)
        return mark_safe(ref_format)

class TypeColumn(tables.Column):
    def render(self, value, record):
        return mark_safe('<span class="'+value.lower()+'-type" title="'+value+'"><span>'+value+'</span></span>')

class ActionColumn(tables.Column):
    empty_values = []
    def render(self, value, record, column, bound_column, bound_row, table):
        actions = ''
        request = None
        for item in table.context:
            if 'request' in item:
                request = item['request']
        if request.session.get('saved') and record.identifier in request.session['saved']:
            method = "remove"
            text = "Remove from saved list"
            button_colour = "red-button"
        else:
            method = "add"
            text = "Add to saved list"
            button_colour = "blue-button"
        has_set = None
        if record.data is not None:
            if hasattr(record.data, 'equation'):
                has_set = record.data.equation
            elif hasattr(record.data, 'percentage') and (record.data.percentage_change != 0 and record.data.percentage_change is not None) and (record.starts_age > 0 and record.ends_age > 0):
                has_set = record.data.percentage
            elif hasattr(record.data, 'dataset'):
                has_set = record.data.dataset
            else:
                actions += ''
        if has_set is not None: 
            actions += '''<form method="post" action="{0}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{1}"/>
                <input type="hidden" name="id" value="{2}" />
                <input type="hidden" name="url" value="{3}" />
                <button class="button {4}" type="submit" title="{5}">{6}</button>
            </form>'''.format(reverse('daa.atlas.views.saved', args=[method]), get_token(request),  record.identifier, request.get_full_path(), button_colour, text, method.title())
        return mark_safe(actions)

class ChangeTable(tables.Table):
    class Meta:
        model = Change
        exclude = ('date_entered', 'gender', 'ends_age', 'description', 'starts_age', 'id', 'process_measured', 'hide', 'equation', 'dataset', 'percentage', 'time_measure')
        sequence = ('identifier', 'name', 'type', 'tissues', 'organism', 'gene', 'data', 'actions')
        attrs = {'class': 'results-table'}
        template = 'table.html'
    
    name = tables.LinkColumn('daa.atlas.views.change', accessor=A('name'), args=[A('identifier')])  
    gene = GeneColumn(verbose_name='Gene', accessor=A('gene.symbol'))
    data = DataColumn(order_by=(A('data.percentage_change'), A('data'), A('dataless_change')))
    tissues = TissueColumn() 
    type = TypeColumn()
    actions = ActionColumn(orderable=False)

class MolecularTable(tables.Table):
    class Meta:
        model = Change
        exclude = ('date_entered', 'gender', 'ends_age', 'description', 'type', 'starts_age', 'process_measured', 'id', 'data_set', 'hide', 'equation', 'dataset', 'percentage', 'time_measure')
        sequence = ('identifier', 'name', 'gene', 'data', 'tissues', 'organism', 'actions') 
        attrs = {'class': 'results-table'}
        template = 'table.html'

    name = tables.LinkColumn('daa.atlas.views.change', args=[A('identifier')])
    gene = GeneColumn()
    data = DataColumn(order_by=(A('data.percentage_change'), A('data'), ))
    tissues = TissueColumn() 
    actions = ActionColumn(orderable=False)

class PathologicalTable(tables.Table):
    class Meta:
        model = Change
        exclude = ('date_entered', 'gender', 'ends_age', 'description', 'type', 'starts_age', 'id', 'gene', 'process_measured', 'hide', 'equation', 'dataset', 'percentage', 'time_measure')
        sequence = ('identifier', 'name', 'data', 'tissues', 'organism', 'actions') 
        attrs = {'class': 'results-table'}
        template = 'table.html'

    name = tables.LinkColumn('daa.atlas.views.change', args=[A('identifier')])
    tissues = TissueColumn()
    data = DataColumn(order_by=(A('data.percentage.percentage_change'), A('data')))
    actions = ActionColumn(orderable=False)

class PhysiologicalTable(tables.Table):
    class Meta:
        model = Change
        exclude = ('date_entered', 'gender', 'ends_age', 'description', 'type', 'starts_age', 'id', 'gene', 'process_measured', 'hide', 'equation', 'dataset', 'percentage', 'time_measure')
        sequence = ('identifier', 'name', 'data', 'tissues', 'organism', 'actions') 
        attrs = {'class': 'results-table'}
        template = 'table.html'

    name = tables.LinkColumn('daa.atlas.views.change', args=[A('identifier')])
    tissues = TissueColumn()
    data = DataColumn(order_by=(A('data.percentage.percentage_change'), A('data')))
    actions = ActionColumn(orderable=False)

class PsychologicalTable(tables.Table):
    class Meta:
        model = Change
        exclude = ('date_entered', 'gender', 'ends_age', 'description', 'type', 'starts_age', 'id', 'gene', 'process_measured', 'hide', 'equation', 'dataset', 'percentage', 'time_measure')
        sequence = ('identifier', 'name', 'data', 'tissues', 'organism', 'actions') 
        attrs = {'class': 'results-table'}
        template = 'table.html'

    name = tables.LinkColumn('daa.atlas.views.change', args=[A('identifier')])
    tissues = TissueColumn()
    data = DataColumn(order_by=(A('data.percentage.percentage_change'), A('data')))
    actions = ActionColumn(orderable=False)

class GeneTable(tables.Table):
    class Meta:
        model = Gene
        exclude = ('id', 'description', 'omim', 'ensembl', 'uniprot', 'unigene', 'go_terms', 'homologs', 'in_genage',)
        sequence = ('entrez_id', 'symbol', 'name', 'alias', 'organism', 'number_of_changes')#'changes_associated')
        attrs = {'class': 'results-table'}
        template = 'table.html'
        order_by = 'symbol'

    name = tables.LinkColumn('daa.atlas.views.gene', args=[A('entrez_id')])
    symbol = tables.LinkColumn('daa.atlas.views.gene', args=[A('entrez_id')])
    number_of_changes = tables.Column(accessor=A('number_of_changes'))#ChangesAssociatedColumn() 
    organism = tables.Column(accessor=A('organism'))

class TissueTable(tables.Table):
    class Meta:
        model = Tissue
        exclude = ('id', 'evid', 'description', 'inInterface', 'rght', 'parent', 'level', 'lft', 'tree_id')
        sequence = ('name', 'synonyms', 'number_of_changes')#'changes_associated')
        attrs = {'class': 'results-table'}
        template = 'table.html'
        order_by = '-number_of_changes'

    name = tables.LinkColumn('daa.atlas.views.tissue', args=[A('evid')])
    #changes_associated = tables.Column(accessor=A('number_of_changes')) #ChangesAssociatedColumn()
    number_of_changes = tables.Column(orderable=True, accessor=A('number_of_changes'))
    #tissue_structure = TissueStructureColumn()

class ReferenceTable(tables.Table):
    class Meta:
        model = Reference
        sequence = ('title', 'author', 'year', 'source', 'number_of_changes')
        exclude = ('id', 'book_title', 'url', 'publisher', 'volume', 'pages', 'journal', 'editor', 'isbn', 'pubmed') 
        attrs = {'class': 'results-table'}
        template = 'table.html'

    number_of_changes = tables.Column(accessor=A('number_of_changes')) #ChangesAssociatedColumn()
    title = ReferenceTitleColumn()
    source = ReferenceSourceColumn(orderable=False)
