from django.db import models
from daa.atlas.admin_widgets import MultiSelectFormField, MultiSelectField

class CellAgeBiblio(models.Model):
    class Meta:
        managed = False
        db_table = 'biblio'
        verbose_name = 'bibliographic reference'
        verbose_name_plural = 'bibliographic references'
        
    pubmed_id = models.IntegerField(primary_key=True)
    terms = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    journal = models.CharField(max_length=500, blank=True, null=True)
    author = models.CharField(max_length=500, blank=True, null=True)
    volume = models.CharField(max_length=500, blank=True, null=True)
    authors = models.CharField(max_length=500, blank=True, null=True)
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
        return str(self.pubmed_id)+": "+author+" "+title

class CellAgeGeneInterventions(models.Model):
    class Meta:
        managed = False
        db_table = 'gene_interventions'
        verbose_name = 'CellAge Gene Intervention'
        verbose_name_plural = 'CellAge Gene Interventions'

    CANCER_YES_NO = (
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Unknown', 'Unknown'),
    )

    SENESCENCE_EFFECT = (
        ('Inhibits', 'Inhibits'),
        ('Promotes', 'Promotes'),
        ('Unclear', 'Unclear'),
    )

    hagr_id = models.AutoField(max_length=11, primary_key=True)
    gene_name = models.CharField(blank=False, null=False, max_length=20)
    hgnc_id = models.IntegerField()
    entrez_id = models.IntegerField()
    organism = models.CharField(blank=False, null=False, max_length=100)
    cancer_type = models.CharField(blank=False, choices=CANCER_YES_NO, null=False, max_length=7)
    description = models.TextField(blank=True, null=True)
    senescence_effect = models.CharField(blank=True, choices=SENESCENCE_EFFECT, null=False, max_length=20)
    notes = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return str(self.hagr_id)

class CellAgeRef(models.Model):
    class Meta:
        managed = False
        db_table = 'ref'
        verbose_name = 'CellAge Reference mapping'
        verbose_name_plural = 'CellAge Reference mappings'

    ref_id = models.AutoField(blank=False, max_length=11, primary_key=True)
    pubmed_id = models.ForeignKey(CellAgeBiblio, db_column='pubmed_id')
    hagr_id = models.ForeignKey(CellAgeGeneInterventions, db_column='hagr_id')

    def __unicode__(self):
        return str(self.ref_id)

class CellAgeCell(models.Model):
    class Meta:
        managed = False
        db_table = 'cell'
        verbose_name = 'CellAge Cells'
        verbose_name_plural = 'CellAge Cell Types'

    cell_type = models.CharField(blank=False, max_length=255, primary_key=True)

    def __unicode__(self):
        return self.cell_type

class CellAgeCellLine(models.Model):
    class Meta:
        managed = False
        db_table = 'cell_line'
        verbose_name = 'CellAge Cell Lines'
        verbose_name_plural = 'CellAge Cell Line Types'

    cell_line_name = models.CharField(blank=False, max_length=100, primary_key=True)

    def __unicode__(self):
        return self.cell_line_name

class CellAgeMethod(models.Model):
    class Meta:
        managed = False
        db_table = 'method'
        verbose_name = 'CellAge Method and Observation Type'
        verbose_name_plural = 'CellAge Method and Observation Types'

    method = models.CharField(max_length=100, blank=False, primary_key=True)

    def __unicode__(self):
        return self.method

class CellAgeSenescence(models.Model):
    class Meta:
        managed = False
        db_table = 'senescence'
        verbose_name = 'CellAge Senescence Type'
        verbose_name_plural = 'CellAge Senescence Types'

    senescence_type = models.CharField(blank=False, max_length=100, primary_key=True)

    def __unicode__(self):
        return self.senescence_type

class CellAgeInterventionMethod(models.Model):
    class Meta:
        managed = False
        db_table = 'intervention_method'
        verbose_name = 'CellAge Intervention Method'
        verbose_name_plural = 'CellAge Intervention Method Types'

    id = models.AutoField(max_length=11, primary_key=True)
    hagr_id = models.ForeignKey(CellAgeGeneInterventions, db_column='hagr_id')
    method = models.ForeignKey(CellAgeMethod, db_column='method')

    def __unicode__(self):
        return str(self.id)

class CellAgeInterventionCell(models.Model):
    class Meta:
        managed = False
        db_table = 'intervention_cell'
        verbose_name = 'CellAge Intervention Cell'
        verbose_name_plural = 'CellAge Intervention Cell Types'

    id = models.AutoField(max_length=11, primary_key=True)
    hagr_id = models.ForeignKey(CellAgeGeneInterventions, db_column='hagr_id')
    cell_type = models.ForeignKey(CellAgeCell, db_column='cell_type')

    def __unicode__(self):
        return str(self.id)

class CellAgeInterventionCellLine(models.Model):
    class Meta:
        managed = False
        db_table = 'intervention_cell_line'
        verbose_name = 'CellAge Intervention Cell Lines'
        verbose_name_plural = 'CellAge Intervention Cell Line Types'

    id = models.AutoField(max_length=11, primary_key=True)
    hagr_id = models.ForeignKey(CellAgeGeneInterventions, db_column='hagr_id')
    cell_line_name = models.ForeignKey(CellAgeCellLine, db_column='cell_line_name')

    def __unicode__(self):
        return str(self.id)

class CellAgeInterventionSenescence(models.Model):
    class Meta:
        managed = False
        db_table = 'intervention_senescence'
        verbose_name = 'CellAge Intervention Senescence'
        verbose_name_plural = 'CellAge Intervention Senescence Types'

    id = models.AutoField(max_length=11, primary_key=True)
    hagr_id = models.ForeignKey(CellAgeGeneInterventions, db_column='hagr_id')
    senescence_type = models.ForeignKey(CellAgeSenescence, db_column='senescence_type')

    def __unicode__(self):
        return str(self.id)

class CellAgeGene(models.Model):
    class Meta:
        managed = False
        db_table = 'gene'
        verbose_name = 'CellAge Gene'
        verbose_name_plural = 'CellAge Genes'
 
    entrez_id = models.IntegerField(primary_key=True)
    gene_symbol = models.CharField(blank=True, null=True, max_length=255)
    gene_name = models.CharField(blank=True, null=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    chr_loc = models.CharField(blank=True, null=True, max_length=50)
    chr_start = models.IntegerField()
    chr_end = models.IntegerField()
    orientation = models.CharField(blank=True, null=True, max_length=50)
    accession = models.CharField(blank=True, null=True, max_length=255)
    unigene = models.CharField(blank=True, null=True, max_length=255)
    omim = models.CharField(blank=True, null=True, max_length=255)
    ensembl = models.CharField(blank=True, null=True, max_length=255)
    hprd = models.CharField(blank=True, null=True, max_length=255)
    species = models.CharField(blank=True, null=True, max_length=100)
    alias = models.CharField(blank=True, null=True, max_length=255)
    homologene = models.CharField(blank=True, null=True, max_length=255)

    def __unicode__(self):
        return str(self.entrez_id)

class CellAgeGo(models.Model):
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

    id = models.AutoField(max_length = 11, primary_key=True)
    entrez_id = models.ForeignKey(CellAgeGene, db_column='entrez_id')
    go = models.IntegerField()
    name = models.TextField(blank=True, null=True)
    go_type = models.CharField(blank=True, null=True, max_length=1, choices=TYPE_CHOICES)

    def __unicode__(self):
        return str(self.id_go)
