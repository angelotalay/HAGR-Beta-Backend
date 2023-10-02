from django.db import models
ASSOC = (
    ('nonsignificant', 'Non-significant',),
    ('significant', 'Significant',),
)

class VariantGroup(models.Model):
    class Meta:
        db_table = 'variantgroup'
    name = models.CharField(max_length=255, blank=True, null=True)
    p_value = models.FloatField(blank=True, null=True)
    association = models.CharField(max_length=20, choices=ASSOC)
    
    def __unicode__(self):
        return u'{}'.format(", ".join([x.__unicode__() for x in self.variant_set.all()]))

class Gene(models.Model):
    class Meta:
        db_table = 'gene'
    entrez_id = models.IntegerField(primary_key=True, blank=False)
    name = models.CharField(max_length=255, db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    alias = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    omim = models.CharField(max_length=20, blank=True, null=True)
    ensembl = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    uniprot = models.CharField(max_length=20, blank=True, null=True)
    unigene = models.CharField(max_length=20, blank=True, null=True)
    in_genage = models.BooleanField(default=False)

    accession = models.CharField(max_length=20, blank=True, null=True)
    cytogenetic_location = models.CharField(max_length=20, blank=True, null=True)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.symbol, self.name)

class Population(models.Model):
    class Meta:
        db_table = 'population'
    name = models.CharField(max_length=255, db_index=True, unique=True)

    def __unicode__(self):
       return u'{}'.format(self.name) 

class Variant(models.Model):
    class Meta:
        db_table = 'variant'

    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('male/female', 'Male/Female'),
    )

    location = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    study_design = models.TextField()
    conclusions = models.TextField()
    odds_ratio = models.FloatField(blank=True, null=True)
    p_value = models.CharField(max_length=100, blank=True, null=True)
    association = models.CharField(max_length=20, choices=ASSOC, blank=True, null=True)
    gender = models.CharField(max_length=15, choices=GENDER, default='male/female')
    studied_number = models.IntegerField(blank=True, null=True)
    control_number = models.IntegerField(blank=True, null=True)
    short_lived_allele = models.CharField(max_length=5, blank=True, null=True)
    long_lived_allele = models.CharField(max_length=5, blank=True, null=True)
    #sample_size = models.IntegerField(blank=True, null=True)

    quickref= models.CharField(max_length=50, db_index=True)
    quickyear= models.IntegerField(db_index=True)
    quickpubmed = models.CharField(max_length=20, db_index=True)

    identifier = models.CharField(max_length=50, null=True, blank=True)
    coordinate =  models.IntegerField(null=True, blank=True)

    gene = models.ForeignKey(Gene, null=True, blank=True)
    population = models.ForeignKey(Population)
    variantgroup = models.ForeignKey(VariantGroup, null=True, blank=True)

    def __unicode__(self):
        return self.location
