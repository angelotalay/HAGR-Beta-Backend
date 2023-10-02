from django.db import models
from daa.atlas.admin_widgets import MultiSelectFormField, MultiSelectField

class Biblio(models.Model):
    class Meta:
        managed = False
        db_table = 'biblio'
        verbose_name = 'model bibliographic reference'
        verbose_name_plural = 'model bibliographic references'
        
    id_biblio = models.AutoField(max_length=4, primary_key=True)
    pubmed = models.IntegerField(blank=True, null=True, unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=100, db_index=True, blank=True)
    publisher = models.CharField(max_length=50, blank=True, null=True)
    volume = models.CharField(max_length=20, blank=True, null=True)
    pages = models.CharField(max_length=20, blank=True, null=True)
    year = models.SmallIntegerField(blank=True, null=True)
    journal = models.CharField(max_length=50, blank=True, null=True)
    editor = models.CharField(max_length=50, blank=True, null=True)
    book_title = models.CharField(max_length=255, blank=True, null=True)
    review = models.SmallIntegerField(blank=True, null=True)

    def issues(self):
        issues = '<ul>'
        if self.longevity_set.count() == 0:
            issues += '<li class="error">This reference is not used by any gene</li>'
        if self.pubmed != '':
            if self.pages == '':
                issues += '<li class="error">Missing page nummbers</li>'
            if self.author == '':
                issues += '<li class="error">Missing author</li>'
            if self.title == '':
                issues += '<li class="error">Missing title</li>'
            if self.year is None:
                issues += '<li class="error">Missing year</li>'
        return issues+'</ul>'
    issues.allow_tags = True
    
    def __unicode__(self):
        title = ''
        author = ''
        if self.title is not None:
            title = self.title
        if self.author is not None:
            author = self.author
        return str(self.pubmed)+": "+author+" "+title
        '''
        if self.pages is not None:
            pgs = ", "+self.pages
        else:
            pgs = ''
        return self.author+". "+str(self.year)+", "+self.title+pgs
        '''

class Model(models.Model):
    class Meta:
        managed = False
        db_table = 'models'
        verbose_name = 'Model Organism'
        verbose_name_plural = 'Model Organisms'
    id_gene = models.AutoField(primary_key=True, max_length=4)
    symbol = models.CharField(max_length=40)
    name = models.CharField(blank=True, null=True, max_length=100)
    organism = models.CharField(max_length=100)
    functions = models.TextField(blank=True, null=True)#CharField(blank=True, null=True, max_length=255)
    entrez_id = models.IntegerField(blank=True, null=True)
    unigene = models.CharField(blank=True, null=True, max_length=30)
    uniprot = models.CharField(blank=True, null=True, max_length=20)
    ensembl = models.CharField(blank=True, null=True, max_length=30)
    alias = models.CharField(blank=True, null=True, max_length=255)

    pubmed = models.TextField(blank=True, null=True, editable=False)

    def issues(self):
        issues = '<ul>'
        if self.symbol == '' or self.symbol is None:
            issues += '<li class="information">Missing a gene symbol</li>'
        if self.name is None or self.name == '':
            issues += '<li class="information">Missing a gene name</li>'
        if self.symbol is not None and self.name is not None:
            if self.symbol.lower() == self.name.lower():
                issues += '<li class="information">Name is the same as gene symbol</li>'
        if self.longevity_set.count() == 0:
            issues += '<li class="error">There are no longevity entries</li>'
        for l in self.longevity_set.all():
            if l.biblio is None:
                issues += '<li class="error">Longevity entry {0} has no reference</li>'.format(l.id)
            if l.phenotype_description == '':
                issues += '<li class="error">Longevity entry {0} has no observations</li>'.format(l.id)
        return issues+'</ul>'
    issues.allow_tags = True
    
    def __unicode__(self):
        return self.symbol+" ("+self.organism+")"

class Longevity(models.Model):
    class Meta:
        managed = False
        db_table = 'longevity'
        verbose_name = 'Longevity Reference'
        verbose_name_plural = 'Longevity References'

    INFLUENCE = (
        ('', 'Unknown'),
        ('anti', 'Anti'),
        ('pro', 'Pro'),
        ('fitness', 'Fitness'),
        ('none', 'None'),
    )

    EFFECT = (
        ('', 'Unknown'),
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('noeffect', 'No Effect'),
    )
    
    id = models.AutoField(primary_key=True)
    lifespan_effect = models.CharField(max_length=30, null=True, blank=True, choices=EFFECT)
    phenotype_description = models.TextField(null=True, blank=True)
    longevity_influence = models.CharField(max_length=10, blank=True, null=True, choices=INFLUENCE)
    max_lifespan_change = models.FloatField(blank=True, null=True)
    max_lifespan_change_desc = models.CharField(max_length=255, blank=True, null=True)
    avg_lifespan_change = models.FloatField(blank=True, null=True)
    avg_lifespan_change_desc = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=255, null=True, blank=True)
    hidden = models.NullBooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    gene = models.ForeignKey(Model)
    biblio = models.ForeignKey(Biblio, null=True, blank=True)

    def __unicode__(self):
        return self.gene.symbol+" ("+self.gene.organism+")"
