from django.db import models
from daa.atlas.admin_widgets import MultiSelectFormField, MultiSelectField

class AnageBiblio(models.Model):
    class Meta:
        managed = False
        db_table = 'biblio'
        verbose_name = 'bibliographic reference'
        verbose_name_plural = 'bibliographic references'
        
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
    
    def __unicode__(self):
        title = ''
        author = ''
        if self.title is not None:
            title = self.title
        if self.author is not None:
            author = self.author
        return str(self.pubmed)+": "+author+" "+title

class AnageDevelopment(models.Model):
    pass

class AnageName(models.Model):
    class Meta:
        managed = False
        db_table = 'names'
        verbose_name = 'Species Longevity'
        verbose_name_plural = 'Species Longevity entries'
    
    KINGDOM_CHOICES = (
        ('Animalia', 'Animalia'),
        ('Monera', 'Monera'),
        ('Protista', 'Protista'),
        ('Plantae', 'Plantae'),
        ('Fungi', 'Fungi'),
    )
        
    id_hagr = models.AutoField(max_length=5, primary_key=True)
    kingdom = models.CharField(max_length=50, choices=KINGDOM_CHOICES)
    phylum = models.CharField(blank=True, null=True, max_length=30)
    class_c = models.CharField(blank=True, null=True, max_length=30, db_column='class')
    subclass = models.CharField(blank=True, null=True, max_length=30)
    infraclass = models.CharField(blank=True, null=True, max_length=30)
    superorder = models.CharField(blank=True, null=True, max_length=30)
    order_c = models.CharField(blank=True, null=True, max_length=30)
    suborder = models.CharField(blank=True, null=True, max_length=30)
    family = models.CharField(blank=True, null=True, max_length=30)
    subfamily = models.CharField(blank=True, null=True, max_length=30)
    genus = models.CharField(blank=True, null=True, max_length=30)
    species = models.CharField(blank=True, null=True, max_length=30)
    name_common = models.CharField(max_length=100)
    synonyms = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name_common
    
class AnageAge(models.Model):
    class Meta:
        managed = False
        db_table = 'age'
        verbose_name_plural = 'Age'
        
    SIZE_SAMPLE_CHOICES = (
        ('tiny', 'Tiny'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('huge', 'Huge'),
    )
    
    QUALITY_CHOICES = (
        ('low', 'Low'),
        ('questionable', 'Questionable'),
        ('acceptable', 'Acceptable'),
        ('high', 'High'),
    )
    
    ORIGIN_CHOICES = (
        ('captivity', 'Captivity'),
        ('wild', 'Wild'),
        ('unknown', 'Unknown'),
    )
    
    hagrid = models.ForeignKey(AnageName, primary_key=True, db_column='hagrid')
    imr = models.FloatField(blank=True, null=True)
    mrdt = models.FloatField(blank=True, null=True)
    tmax = models.FloatField(blank=True, null=True)
    size_sample = models.CharField(max_length=20, choices=SIZE_SAMPLE_CHOICES)
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES)
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES)
    biblioid = models.ForeignKey(AnageBiblio, db_column='biblioid', blank=True, null=True)
    phenotype = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.hagrid.name_common
    
class AnageLinks(models.Model):
    class Meta:
        managed = False
        db_table = 'links'
        verbose_name_plural = 'links'
    hagrid = models.ForeignKey(AnageName, primary_key=True, db_column='hagrid')
    adw = models.SmallIntegerField(blank=True, null=True)
    itis = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.hagrid.name_common
    
class AnageMetabolism(models.Model):
    class Meta:
        managed = False
        db_table = 'metabolism'
        verbose_name_plural = 'metabolism'
    hagrid = models.ForeignKey(AnageName, primary_key=True, db_column='hagrid')
    temperature = models.FloatField(blank=True, null=True)
    metabolic_rate = models.FloatField(blank=True, null=True)
    body_mass = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.hagrid.name_common
    
class AnageRef(models.Model):
    class Meta:
        managed = False
        db_table = 'refs'
        verbose_name = 'reference'
        verbose_name_plural = 'references'
    id_refs = models.AutoField(max_length=4, primary_key=True)
    hagrid = models.ForeignKey(AnageName, db_column='hagrid')
    id_biblio = models.ForeignKey(AnageBiblio, db_column='id_biblio')
