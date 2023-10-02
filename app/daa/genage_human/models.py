from django.db import models
from daa.atlas.admin_widgets import MultiSelectFormField, MultiSelectField

class Biblio(models.Model):
    class Meta:
        managed = False
        db_table = 'biblio'
        verbose_name = 'human bibliographic reference'
        verbose_name_plural = 'human bibliographic references'
        
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
        if self.ref_set.count() == 0:
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

class Name(models.Model):
    class Meta:
        managed = False
        db_table = 'names'
        verbose_name = 'Human Ageing Gene'
        verbose_name_plural =  'Human Ageing Genes'
    id_hagr = models.AutoField(max_length=4, primary_key=True, db_column='id_hagr')
    aliases = models.CharField(blank=True, null=True, max_length =255)
    symbol_hugo = models.CharField(blank=True, null=True, max_length=10)
    name_common = models.CharField(blank=True, null=True, max_length=200)
    entrez_id = models.IntegerField()
    pubmed = models.TextField(blank=True, null=True, editable=False)
    
    refs = models.ManyToManyField(Biblio, through='Ref')
    
    def __unicode__(self):
        return self.name_common
        
class Features(models.Model):
    class Meta:
        managed = False
        db_table = 'features'
        verbose_name_plural = 'Features'
        
    WHY_CHOICES = (
        ('human', 'Human'),
        ('mammal', 'Mammal'),
        ('human_link','Human Linked'),
        ('model', 'Model'),
        ('cell', 'Cell'),
        ('functional', 'Functional'),
        ('upstream','Upstream'),
        ('downstream','Downstream'),
        ('putative','Putative'),
    )
    FUNCTIONS_CHOICES = (
        ('DNA_repair','DNA_repair'),
        ('DNA_condensation','DNA condensation'),
        ('DNA_replication','DNA replication'),
        ('energy_apparatus','Energy apparatus'),
        ('apoptosis','Apoptosis'),
        ('stress_response','Stress_response'),
        ('redox_and_oxidative_regulation','Redox and oxidative regulation'),
        ('transcriptional_regulation','Transcriptional regulation'),
        ('cell_cycle_control','Cell cycle control'),
        ('growth_and_development','Growth and development'),
        ('calcium_metabolism','Calcium metabolism'),
        ('signalling','Signalling'),
        ('other', 'Other'),
    )
    hagrid = models.ForeignKey(Name, db_column='hagrid')
    why = MultiSelectField(max_length=100, choices=WHY_CHOICES)
    band = models.CharField(blank=True, null=True, max_length=10)
    location_start = models.IntegerField(blank=True, null=True)
    location_end = models.IntegerField(blank=True, null=True)
    orientation = models.IntegerField(blank=True, null=True)
    phenotype = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.hagrid.name_common

class Go(models.Model):
    class Meta:
        managed = False
        db_table = 'go'
        verbose_name = 'GO Term'
        verbose_name_plural = 'GO Terms'
    TYPE_CHOICES = (
        ('P', 'Process'),
        ('F', 'Function'),
        ('C', 'Component'),
    )
    id_go = models.AutoField(max_length = 5, primary_key=True)
    hagrid = models.ForeignKey(Name, db_column='hagrid')
    go = models.IntegerField()
    name = models.TextField(blank=True, null=True)
    type = models.CharField(blank=True, null=True, max_length=1, choices=TYPE_CHOICES)
    
    def __unicode__(self):
        return self.hagrid.name_common+" - "+str(self.go)
    
class Homolog(models.Model):
    class Meta:
        managed = False
        db_table = 'homologs'
    id_homol = models.IntegerField(primary_key=True)
    hagrid = models.ForeignKey(Name, db_column='hagrid')
    organism = models.CharField(max_length=50)
    gene_id = models.CharField(blank=True, null=True, max_length=20)
    gene_symbol = models.CharField(blank=True, null=True, max_length=20)
    gene_name = models.CharField(blank=True, null=True, max_length=200)
    
    def __unicode__(self):
        return self.hagrid.name_common+" - "+self.organism+", "+self.gene_symbol
    
class Interaction(models.Model):
    class Meta:
        managed = False
        db_table = 'interactions'
    id_inter = models.AutoField(max_length=5, primary_key=True)
    hagrid_one = models.ForeignKey(Name, related_name='hagrid_one', db_column='hagrid_one')
    hagrid_two = models.ForeignKey(Name, related_name='hagrid_two', db_column='hagrid_two')
    type = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.hagrid_one.name_common+" interacting with "+self.hagrid_two.name_common
    
class Links(models.Model):
    class Meta:
        managed = False
        db_table = 'links'
        verbose_name_plural = 'Links'
    hagrid = models.ForeignKey(Name, db_column='hagrid')
    omim = models.IntegerField(blank=True, null=True)
    hprd = models.CharField(blank=True, null=True, max_length=5)
    unigene = models.IntegerField(blank=True, null=True)
    entrez_gene = models.IntegerField(blank=True, null=True)
    homologene = models.IntegerField(blank=True, null=True)
    swissprot = models.CharField(blank=True, null=True, max_length=20)
    sageke = models.IntegerField(blank=True, null=True)
    ensembl = models.CharField(blank=True, null=True, max_length=30)
    
    def __unicode__(self):
        return self.hagrid.name_common
    
class Microarray(models.Model):
    class Meta:
        managed = False
        db_table = 'microarray'
    entrez_id = models.IntegerField(primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=255)
    symbol = models.CharField(blank=True, null=True, max_length=10)
    overexpressed = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return str(self.entrez_id)+" - "+self.symbol+", "+self.name
    
class Ref(models.Model):
    class Meta:
        managed = False
        db_table = 'refs'
    id_refs = models.AutoField(primary_key = True, max_length = 5)
    hagrid = models.ForeignKey(Name, db_column='hagrid')
    id_biblio = models.ForeignKey(Biblio, db_column='id_biblio')
    
class Sequence(models.Model):
    class Meta:
        managed = False
        db_table = 'sequences'
    hagrid = models.ForeignKey(Name, db_column='hagrid')
    seq_promoter = models.TextField(blank=True, null=True)
    acc_promoter = models.CharField(blank=True, null=True, max_length=16)
    seq_orf = models.TextField(blank=True, null=True)
    acc_orf = models.CharField(blank=True, null=True, max_length=16)
    seq_cds = models.TextField(blank=True, null=True)
    acc_cds = models.CharField(blank=True, null=True, max_length=16)
    
    def __unicode__(self):
        return self.hagrid.name_common
