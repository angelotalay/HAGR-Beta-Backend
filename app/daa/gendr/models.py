from django.db import models

class Biblio(models.Model):
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

    def issues(self):
        issues = '<ul>'
        if self.bibliogene_set.count() == 0:
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

class Gene(models.Model):
    class Meta:
        managed = False
        db_table = 'genes'
        verbose_name = 'gene manipulation'
        verbose_name_plural = 'gene manipulations'
    SPECIES = (
        ('Caenorhabditis elegans', 'Caenorhabditis elegans'),
        ('Drosophila melanogaster','Drosophila melanogaster'),
        ('Mus musculus','Mus musculus'),
        ('Saccharomyces cerevisiae','Saccharomyces cerevisiae'),
        ('Schizosaccharomyces pombe', 'Schizosaccharomyces pombe'),
    )
    id = models.AutoField(max_length=11, primary_key=True)
    entrez_id = models.IntegerField(unique=True)
    gene_symbol = models.CharField(max_length=10)
    gene_name = models.CharField(max_length=255, null=True, blank=True)
    species_name = models.CharField(max_length=100, choices=SPECIES)
    description = models.TextField()
    gene_id = models.CharField(max_length=20, null=True, blank=True)
    ensembl = models.CharField(max_length=30, null=True, blank=True)
    pubmed = models.TextField(null=True, blank=True)
    alias = models.CharField(max_length=255, blank=True, null=True)
    function = models.TextField(blank=True,null=True)

    def issues(self):
        issues = '<ul>'
        if self.pmid.count() == 0:
            issues += '<li class="error">Missing a reference</li>'
        if self.gene_name == '':
            issues += '<li class="information">Missing a name</li>'
        if self.gene_symbol == '':
            issues += '<li class="information">Missing a gene symbol</li>'
        if self.description == '':
            issues += '<li class="error">Missing a description</li>'
        if self.species_name == '':
            issues += '<li class="error">Not assigned a species</li>'
        if self.entrez_id is None:
            issues += '<li class="error">Missing an entrez_id</li>'
        return issues+'</ul>'
    issues.allow_tags = True


    def __unicode__(self):
        return "{0} {1}".format(self.gene_symbol, self.species_name)

class BiblioGene(models.Model): 
    class Meta:
        managed = False
        db_table = 'biblio_genes'
    biblio_id = models.ForeignKey(Biblio, db_column='biblio_id', to_field='id_biblio')
    entrez_id = models.ForeignKey(Gene, db_column='entrez_id', to_field='entrez_id')

class Expression(models.Model):
    class Meta:
        managed = False
        db_table = 'expression'
        verbose_name = 'gene expression'
        verbose_name_plural = 'gene expressions'
    mapping = models.IntegerField(null=True)
    gene_symbol = models.CharField(max_length=10, null=True)
    gene_name = models.CharField(max_length=255, null=True)
    entrez_id = models.IntegerField(primary_key=True)
    total = models.IntegerField(null=True)
    overexp = models.IntegerField(null=True)
    underexp = models.IntegerField(null=True)
    p_value = models.DecimalField(max_digits=100, decimal_places=50, null=True)
    classification = models.CharField(max_length=20, null=True)
    ensembl = models.CharField(max_length=30, blank=True, null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.gene_symbol
