import datetime
import re

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.safestring import mark_safe
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey
from daa.django_libage.models import Citation

class GOTerm(models.Model):
    CATEGORIES = (
        ('process', 'process'),
        ('function', 'function'),
        ('component', 'component'),
    )

    id = models.PositiveIntegerField(primary_key=True)
    term = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORIES)

    class Meta:
        managed = False

    def __unicode__(self):
        return str(self.id)+': '+self.term

class Organism(models.Model):
    class Meta:
        ordering = ['common_name']
        managed = False

    taxonomy_id = models.PositiveIntegerField(db_index=True)
    name = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50, blank=True, null=True)
    hasDatabase = models.BooleanField()

    def __unicode__(self):
        '''
        end = ''
        if self.common_name != '':
            end = ' ('+self.common_name+')'
        return self.name+end
        '''
        if self.common_name != '':
            return self.common_name
        else:
            return self.name
    managed=False

class Homolog(models.Model):
    class Meta:
        managed = False

    symbol = models.CharField(max_length=20)
    entrez_id = models.PositiveIntegerField()

    organism = models.ForeignKey(Organism)

    def __unicode__(self):
        return self.symbol+' ('+self.organism.name+')'

def get_human_organism():
    return Organism.objects.get(taxonomy_id=9606)

class Gene(models.Model):
    class Meta:
        managed = False

    entrez_id = models.PositiveIntegerField(db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    alias = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    omim = models.CharField(max_length=20, blank=True, null=True)
    ensembl = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    uniprot = models.CharField(max_length=20, blank=True, null=True)
    unigene = models.CharField(max_length=20, blank=True, null=True)
    in_genage = models.BooleanField(default=False)

    organism = models.ForeignKey(Organism, default=get_human_organism)

    def compound_name(self):
        if self.symbol.strip() == '':
            name = self.name
        else:
            name = u'{} ({})'.format(self.symbol, self.name)
        return name

    def __unicode__(self):
        return self.symbol+' ('+self.name+')'

def generate_evid():
    try:
        last_id = Tissue.objects.order_by('evid')
        if last_id.count() > 0:
            last = last_id[last_id.count()-1]
            return last.evid+1
        else:
            return 1 
    except:
        return 0

class Tissue(MPTTModel):

    class MPTTMeta:
        order_insertion_by = ['evid']
    class Meta:
        managed = False

    evid = models.PositiveIntegerField(default=generate_evid)
    name = models.CharField(max_length=50, db_index=True)
    synonyms = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    inInterface = models.BooleanField(default=False)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __unicode__(self):
        return self.name

class PropertyGroup(models.Model):
    class Meta:
        managed = False

    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Property(models.Model):
    class Meta:
        ordering = ['group']
        managed = False

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    group = models.ForeignKey(PropertyGroup)

    def __unicode__(self):
        return self.name

class Reference(models.Model):
    class Meta:
        ordering = ['-year']
        managed = False

    pubmed = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    url = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    publisher = models.CharField(max_length=50, blank=True, null=True)
    volume = models.CharField(max_length=20, blank=True, null=True)
    pages = models.CharField(max_length=20, blank=True, null=True)
    year = models.PositiveIntegerField()
    journal = models.CharField(max_length=50, blank=True, null=True)
    editor = models.CharField(max_length=50, blank=True, null=True)
    book_title = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)

    def formatted_reference(self):
        if self.author != '':
            persons = self.author
        elif self.editor != '':
            persons = self.editor+' (editor)'
        else:
            persons = u''

        if self.pubmed != '' and self.pubmed is not None:
            link = u' (<a href="http://www.ncbi.nlm.nih.gov/pubmed/{0}">Pubmed</a>)'.format(self.pubmed)
        elif self.url != '':
            link = u' (<a href="{0}">{0}</a>)'.format(self.url)
        else:
            link = u''

        ref_format = u''
        if self.book_title != u'':
            ref_format = u'<i>{0} (editor)</i>. ({1}) {2}'.format(self.editor, str(self.year), self.book_title)
        else:
            ref_format = u'<i>{0}</i> ({1}) "{2}" <i>{3}</i> <b>{4}</b> {5} {6}'.format(persons, str(self.year), self.title, self.journal, self.volume, self.pages, link)
            
        return mark_safe(ref_format)    

    def __unicode__(self):
        if self.author != '':
            persons = self.author   
        elif self.editor != '':
            persons = self.editor+' (editor)'
        else:
            persons = ''
    
        ref_format = ''
        if self.book_title != '':
            ref_format = self.editor+' (editor). ('+str(self.year)+') '+self.book_title
        else:
            ref_format = persons+' ('+str(self.year)+') "'+self.title+'" '+self.journal+' '+self.volume+' '+self.pages
            
        return ref_format 

class Person(models.Model):
    class Meta:
        managed = False

    name = models.CharField(max_length=50)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __unicode__(self):
        return self.name

class ProcessMeasured(models.Model):
    class Meta:
        managed = False

    name = models.CharField(max_length=100, db_index=True)

    def __unicode__(self):
        return self.name

class Data(models.Model):
    
    class Meta:
        managed = False

    TYPE = (
        ('percentage', 'Percentage Change'),
        ('equation', 'Equation'),
        ('series', 'Series'),
        ('incidence', 'Incidence Series'),
        ('morbidity', 'Morbidity Series'),
    )
    PLOT = (
        ('none', 'Do not plot'),
        ('linear', 'Linear Line'),
        ('exponential', 'Exponential Line'),
        ('line', 'Line'),
        ('bar', 'Bar'),
        ('column', 'Column'),
        ('point', 'Point'),
        ('pie', 'Pie'),
    )

    type = models.CharField(max_length=20, choices=TYPE)
    plot = models.CharField(max_length=20, choices=PLOT, default='none')
    sample_size = models.IntegerField(blank=True, null=True)
    measure = models.CharField(max_length=30, blank=True, null=True)
    method_collection = models.CharField(max_length=50, blank=True, null=True)
    data_transforms = models.CharField(max_length=50, blank=True, null=True)

    percentage_change = models.FloatField(null=True, blank=True)
    p_value = models.DecimalField(max_digits=30, decimal_places=25, blank=True, null=True)

    def get_pvalue(self):
        return self.p_value

    def __unicode__(self):
        if hasattr(self, 'percentage'):
            return self.percentage.__unicode__()
        elif hasattr(self, 'equation'):
            return self.equation.__unicode__()
        elif hasattr(self, 'dataset'):
            return self.dataset.__unicode__()
        return 'Data' 

class DataPoint(models.Model):
    class Meta:
        ordering = ['label']
        managed = False

    label = models.CharField(max_length=20)
    point = models.FloatField()

    part_of = models.ForeignKey(Data)

    def __unicode__(self):
        return self.label+' '+str(self.point)

class Percentage(Data):
    class Meta:
        managed = False

    is_negative = models.BooleanField(verbose_name="Is negative or decreases")

    def __unicode__(self):
        try:
            return self.change_set.all()[0].name
        except:
            return 'Percentage'

class Equation(Data):
    class Meta:
        managed = False

    coefficiant = models.DecimalField(max_digits=30, decimal_places=25)
    intercept = models.DecimalField(max_digits=30, decimal_places=25)

    is_negative = models.BooleanField()
    # NEED TO DEPRECATE
    p_value_d = models.DecimalField(max_digits=30, decimal_places=25, blank=True, null=True)

    def __unicode__(self):
        try:
            return self.change_set.all()[0].name
        except:
            return 'Equation'

class Dataset(Data):
    class Meta:
        managed = False

    def __unicode__(self):
        try:
            return self.change_set.all()[0].name
        except:
            return 'Dataset'
        #return 'Dataset: '+self.change_dataset.all()[0].name

class PercentageManager(models.Manager):
    class Meta:
        managed = False

    def get_query_set(self):
        return super(PercentageManager, self).get_query_set()

def generate_identifier():
    try:
        last_id = Change.objects.only('id').order_by('id')
        if last_id.count() > 0:
            last = last_id[last_id.count()-1]
            return 'DAA'+str(last.id+1)
        else:
            return 'DAA1'
    except:
        return 'ERROR'

class Change(models.Model):

    class Meta:
        ordering = ('name', 'type',)
        managed = False
 
    CHANGE_TYPE = (
        (u'physiological', u'Physiological'),
        (u'molecular', u'Molecular'),
        (u'pathological', u'Pathological'),
        (u'psychological', u'Psychological'),
    )   
    
    GENDER = (
        (u'male', u'Male'),
        (u'female', u'Female'),
        (u'male/female', u'Male/Female'),
    )

    TIME_MEASURE = (
        (u'years', u'Years'),
        (u'months', u'Months'),
    )

    identifier = models.CharField(max_length=20, default=generate_identifier)
    name = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=15, choices=CHANGE_TYPE, help_text='As a hint, changes to a gene (e.g. gene expression, proteomics) are usually molecular, changes that occur whole body, such as hormonal changes, are physiological', db_index=True)
    gender = models.CharField(max_length=15, choices=GENDER, default=u'male/female')
    date_entered = models.DateTimeField(default=timezone.now)
    starts_age = models.IntegerField(help_text='Use -1 if you don\'t know the actual start date.')
    ends_age = models.IntegerField(help_text='Use -1 if you don\'t know the end date. If both of the fields contain -1, a message will be displayed that the age this occurs is unknown.')
    time_measure = models.CharField(max_length=10, choices=TIME_MEASURE, default='years')
    description = models.TextField(blank=True, null=True, help_text='You can use Markdown formatting in this field. See <a href="http://daringfireball.net/projects/markdown/syntax">here for more details</a>. Basically, paragraphs will be kept, _word_ for italic, **word** for bold, [words here](http://ageing-map.org) for a link.')
    hide = models.BooleanField(default=False, help_text="Hides the change from the interface but leaves it present in the database")

    gene = models.ForeignKey(Gene, blank=True, null=True, help_text='If the change is associated with a gene, include it here. (<b>Note:</b> The change does not have to directly be affected by the gene, for example hormone levels)', db_index=True)
    organism = models.ForeignKey(Organism, help_text='The organism in which the change takes place', db_index=True)
    process_measured = models.ForeignKey(ProcessMeasured, blank=True, null=True, help_text='What is being measured? (<b>Note:</b> This does not require data to be associated with the change as long as the description contains the information)', db_index=True)

    data = models.ForeignKey(Data, blank=True, null=True, help_text='There are 3 different types of data you can add: <ul><li><b>Percentages:</b> A percentage change and a p value indicating confidence</li><li><b>Equation:</b> An equation describing the change in mathematical terms. Requires a coefficient, intercept as well as p value and percentage change</li><li><b>Dataset:</b> A series of values (for instance points or quantities) describing a set of data. Can be used for bar charts, curves etc. that require more detail than an equation</li></ul>')
    
    tissues = models.ManyToManyField(Tissue, help_text='All changes must be associated with a tissue. There is an option for "whole body" if the change occurs body-wide', db_index=True)
    properties = models.ManyToManyField(Property, blank=True)
    people = models.ManyToManyField(Person, blank=True)

    def description_with_references(self):
        return mark_safe(re.sub(r'\[(\d+)\]', r'[<a href="/atlas/reference/\1/">\1</a>]', self.description))

    def issues(self):
        issues = '<ul>'
        try:
            if self.gene.symbol == '':
                issues += '<li class="information">Missing a gene symbol</li>'
        except: 
            pass
        if self.tissues.count() == 0:
            issues += '<li class="error">Missing a tissue</li>'
        if self.name == '':
            issues += '<li class="error">The change does not have a name</li>'
        if (self.type == 'physiological' or self.type == 'psychological') and self.description == '':
            issues += '<li class="warning">The change does not have any descriptive text</li>'
        return issues+'</ul>'
    issues.allow_tags = True

    def delete(self, *args, **kwargs):
        super(Change, self).delete(*args, **kwargs)
        try:
            citation = Citation.objects.get(identifier=self.identifier)
            citation.delete()
        except:
            pass

    def __unicode__(self):
        return self.identifier+': '+self.name 

class Image(models.Model):
    class Meta:
        managed = False
    change = models.ForeignKey(Change, null=True)
    image = models.ImageField(upload_to='change_images/')
    caption = models.TextField(blank=True, null=True, help_text="An optional caption displayed under the image, supports markdown formatting")


class Relationship(MPTTModel):
    class Meta:
        managed = False
    TYPE = (
        ('etiology', 'Etiology'),
        ('definition', 'Definition'),
    )

    type = models.CharField(max_length=20, choices=TYPE, null=True, blank=True, help_text='This had a purpose at one time, but I no longer know what any of these terms mean. Best ignoring it.')

    change = models.ForeignKey(Change, null=True, related_name='Change', help_text='The change to which this relationship applies. If you are creating a heirarchy you create a relationship linked to change first, then create more relationships as children.')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', help_text='The parent of this relationship. Changing this simply move it and all of its children to the new tree. If one isn\'t give, this change is assumed to be the parent.')

    references = models.ManyToManyField(Reference, blank=True, help_text='Futher evidence linking the changes in this relationship.')

    def __unicode__(self):
        '''
        try:
            parent = self.parent.change.name
            parent = ' to '+parent
        except AttributeError:
            parent = ' (relationship parent)'
        '''
        return u"{0} (RID: {1})".format(self.change.name , self.id)

class Note(models.Model):
    class Meta:
        managed = False
    date_added = models.DateTimeField(default=timezone.now) 
    text = models.TextField()

    person = models.ForeignKey(Person)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.text
