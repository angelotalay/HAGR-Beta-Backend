from django.db import models
from daa.atlas.admin_widgets import MultiSelectFormField, MultiSelectField

class DrugAgeBiblio(models.Model):
    class Meta:
        managed = False
        db_table = 'biblio'
        verbose_name = 'bibliographic reference'
        verbose_name_plural = 'bibliographic references'
        
    id_biblio = models.AutoField(max_length=11, primary_key=True)
    terms = models.CharField(max_length=500, blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    journal = models.CharField(max_length=500, blank=True, null=True)
    author = models.CharField(max_length=500, blank=True, null=True)
    volume = models.CharField(max_length=500, blank=True, null=True)
    authors = models.CharField(max_length=500, blank=True, null=True)
    pubmed = models.IntegerField(blank=False, null=False, unique=True)
    author_initials = models.CharField(max_length=500, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    contact_addresses = models.CharField(max_length=500, blank=True, null=True)
    issue = models.CharField(max_length=500, blank=True, null=True)
    pages = models.CharField(max_length=500, blank=True, null=True)
    editor = models.CharField(max_length=500, blank=True, null=True)
    review = models.CharField(max_length=500, blank=True, null=True)
    publisher = models.CharField(max_length=500, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)
    
    def __unicode__(self):
        title = ''
        author = ''
        if self.title is not None:
            title = self.title
        if self.author is not None:
            author = self.author
        return str(self.pubmed)+": "+author+" "+title

class DrugAgeCompounds(models.Model):
    class Meta:
        managed = False
        db_table = 'compounds'
        verbose_name = 'Compounds'
        verbose_name_plural = 'Compounds'

    id = models.AutoField(max_length=11, primary_key=True)
    compound_name = models.CharField(blank=True, null=True, max_length=255)
    cas_number = models.CharField(blank=True, null=True, max_length=25)
    pubchem_cid = models.IntegerField(max_length=10, blank=True, null=True)
    iupac_name = models.CharField(blank=True, null=True, max_length=800)

    def __unicode__(self):
        return unicode("%d %s" % (self.id, self.compound_name))


class DrugAgeLifespan(models.Model):
    p_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    class Meta:
        abstract = True

class MaxLifespan(DrugAgeLifespan):
    """ UNUSED FOR NOW AS THERE ARE OTHER COLUMNS THAT HAVE THIS INFORMATION.
    This is for the max_lifespan_change_percent column in the results table that utilises an intermediary table to contain its p-values.
    """
    max_lifespan_change_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'max_lifespan'
        verbose_name = 'Max Lifespan (% Change)'
    def __str__(self):
        return "{} : p-value={}".format(self.max_lifespan_change_percent, self.p_value)

class AverageLifespan(DrugAgeLifespan):
    """ UNUSED FOR NOW AS THERE ARE OTHER COLUMNS THAT HAVE THIS INFORMATION.
    This is for the average_lifespan_change_percent column in the results table that utilises an intermediary table to contain its p-values.
    """
    average_lifespan_change_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    class Meta:
        managed= True
        db_table = 'average_lifespan'
        verbose_name = 'Average Lifespan (% Change)'
    def __str__(self):
        return "{} : p-value={}".format(self.average_lifespan_change_percent, self.p_value)


class DrugAgeResults(models.Model):
    class Meta:
        managed = True
        db_table = 'results'
        verbose_name = 'Results'
        verbose_name_plural = 'Results'
       
    GENDER_CHOICES = (
      ('MALE', 'Male'),
      ('FEMALE', 'Female'),
      ('BOTH', 'Mixed'),
      ('HERMAPHRODITE', 'Hermaphrodite'),
    )  

    SIG_CHOICES = (
      ('S', 'Significant'),
      ('NS', 'Non-significant'),
      ('', ''),
    )

    P_VALUE_CHOICES = (
        ("NS", "Non-significant"),
        ("p<0.05", "p<0.05"),
        ("p<0.01", "p<0.01"),
        ("p<0.001", "p<0.001"),
        ("p<0.0001", "p<0.0001")
    )

    id = models.AutoField(max_length=11, primary_key=True)
    compound_id = models.ForeignKey(DrugAgeCompounds, db_column='compound_id', on_delete=models.CASCADE, verbose_name = "compound")
    species = models.CharField(blank=True, null=True, max_length=255)
    age_at_initiation = models.CharField(blank=True, null=True, max_length=20, verbose_name="age at initiation of treatment")
    gender = models.CharField(blank=True, null=True, choices=GENDER_CHOICES, max_length=15)
    strain = models.CharField(blank=True, null=True, max_length=255)
    dosage = models.CharField(blank=True, null=True, max_length=100)
    avg_lifespan_change_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    avg_lifespan_p_value = models.CharField(choices=P_VALUE_CHOICES, max_length=10 ,  blank=True, null=True)
    max_lifespan_change_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    max_lifespan_p_value = models.CharField(choices=P_VALUE_CHOICES, max_length=10 ,blank=True, null=True)
    significance = models.CharField(null=True, blank=True,choices=SIG_CHOICES, max_length=255)
    pubmed_id = models.IntegerField(max_length=11, null=False)
    notes = models.CharField(blank=True, null=True, max_length=2000)
    last_modified = models.DateTimeField(auto_now=True)
    biblio_id = models.ForeignKey(DrugAgeBiblio, db_column='biblio_id', on_delete=models.CASCADE, blank=True, null=True)

    def __unicode__(self):
        compound_name = unicode(self.compound_id)
        return compound_name
    def __str__(self):
        return self.__unicode__().encode('utf-8')

class DrugAgeCompoundSynonyms(models.Model):
    class Meta:
        managed = False
        db_table = 'compound_synonyms'
        verbose_name = 'Synonyms'
        verbose_name_plural = 'Synonyms'

    id = models.AutoField(max_length=11, primary_key=True)
    compound_id = models.ForeignKey(DrugAgeCompounds, db_column='compound_id', on_delete=models.CASCADE)
    synonym = models.CharField(max_length=500)

    def __unicode__(self):
        return str(self.compound_id)
