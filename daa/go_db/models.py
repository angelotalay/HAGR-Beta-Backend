from django.db import models

class Term(models.Model):
	class Meta:
		managed = False
		#db_table = u'term'

	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255)
	term_type = models.CharField(max_length=55, db_index=True)
	acc = models.CharField(max_length=255)
	is_obsolete = models.IntegerField(default=0)
	is_root = models.IntegerField(default=0)
	is_relation = models.IntegerField(default=0)

	def __unicode__(self):
		return u"{0}: {1}".format(self.acc, self.name)

class DB(models.Model):
	class Meta:
		managed = False
		#db_table = u'db'

	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=55, unique=True, blank=True, null=True)
	fullname = models.CharField(max_length=255, blank=True, null=True)
	datatype = models.CharField(max_length=255, blank=True, null=True)
	generic_url = models.CharField(max_length=255, blank=True, null=True)
	url_syntax = models.CharField(max_length=255, blank=True, null=True)
	url_example = models.CharField(max_length=255, blank=True, null=True)
	uri_prefix = models.CharField(max_length=255, blank=True, null=True)

class DBxref(models.Model):
	class Meta:
		managed = False
		#db_table = u'DBxref'

	id = models.AutoField(primary_key=True)
	xref_dbname = models.ForeignKey(DB, to_field='name', db_column='xref_dbname')
	xref_key = models.CharField(max_length=255)
	xref_keytype = models.CharField(max_length=32, blank=True, null=True)
	xref_desc = models.CharField(max_length=255, blank=True, null=True)

class Species(models.Model):
	class Meta:
		managed = False
		#db_table = u'species'

	id = models.AutoField(primary_key=True)
	ncbi_taxa_id = models.IntegerField()
	common_name = models.CharField(max_length=255, blank=True, null=True)
	lineage_string = models.TextField(blank=True, null=True)
	genus = models.CharField(max_length=55, blank=True, null=True)
	species = models.CharField(max_length=255, blank=True, null=True)
	parent_id = models.IntegerField(blank=True, null=True)
	left_value = models.IntegerField(blank=True, null=True)
	right_value = models.IntegerField(blank=True, null=True)
	taxonomic_rank = models.CharField(max_length=255)

class GeneProduct(models.Model):
	class Meta:
		managed = False
		#db_table = u'gene_product'

	id = models.AutoField(primary_key=True)
	symbol = models.CharField(max_length=128)
	dbxref = models.ForeignKey(DBxref, db_column='dbxref_id')
	species = models.ForeignKey(Species, blank=True, null=True, db_column='species_id')
	type = models.IntegerField(blank=True, null=True, db_column='type_id')
	full_name = models.TextField(blank=True, null=True)

	def __unicode__(self):
		return u'{0} ({1})'.format(self.symbol, self.species.common_name)

class Association(models.Model):
	class Meta:
		managed = False
		#db_table = u'association'

	id = models.AutoField(primary_key=True)
	term = models.ForeignKey(Term, db_column='term_id')
	gene_product = models.ForeignKey(GeneProduct, db_column='gene_product_id')
