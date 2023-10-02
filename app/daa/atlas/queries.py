from django.db.models import Q  

def change_query(s):
	return Q(name__icontains=s)|Q(gene__entrez_id__icontains=s)|Q(gene__ensembl__icontains=s)|Q(gene__name__icontains=s)|Q(gene__symbol__icontains=s)|Q(process_measured__name__icontains=s)|Q(identifier__icontains=s)

def tissue_query(s):
	return Q(name__icontains=s)|Q(synonyms__icontains=s)

def gene_query(s):
	return Q(entrez_id__icontains=s)|Q(name__icontains=s)|Q(symbol__icontains=s)|Q(alias__icontains=s)|Q(ensembl__icontains=s)

def reference_query(s):
	return Q(title__icontains=s)|Q(author__icontains=s)|Q(journal__icontains=s)|Q(year__icontains=s)	

