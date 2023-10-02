from django.db import models

class Ortholog(models.Model):
    class Meta:
        managed = False
        db_table = 'ortholog'
    entrez_a = models.IntegerField(null=True)
    symbol_a = models.CharField(max_length=20, null=True)
    ensembl_a = models.CharField(max_length=20, null=True)
    uniprot_a = models.CharField(max_length=10)
    species_a = models.CharField(max_length=50)
    score_a = models.FloatField()
    entrez_b = models.IntegerField(null=True)
    symbol_b = models.CharField(max_length=20, null=True)
    ensembl_b = models.CharField(max_length=20, null=True)
    uniprot_b = models.CharField(max_length=10)
    species_b = models.CharField(max_length=50)
    score_b = models.FloatField()

