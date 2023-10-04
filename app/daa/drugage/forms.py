from django import forms
from .models import DrugAgeResults, DrugAgeBiblio
from daa.tools.fetch_pmid import get_pmid_information, PMIDRequestException


class DrugAgeResultsForm(forms.ModelForm):
    pubmed_id = forms.CharField(required=True, label="PubMed ID")

    class Meta:
        model = DrugAgeResults
        fields = "__all__"

    def clean_pubmed_id(self):
        pubmed_id = self.cleaned_data['pubmed_id']
        if not pubmed_id.isdigit():
            raise forms.ValidationError("PubMed ID must be a number.")
        if not (0 < int(pubmed_id) < 10 ** 10):
            raise forms.ValidationError("Please enter a valid PubMed ID.")
        try:
            biblio_data = get_pmid_information(pubmed_id)
        except PMIDRequestException:
            raise forms.ValidationError("PubMed ID not found.")

        try:
            # Try to get the existing entry
            biblio_entry = DrugAgeBiblio.objects.get(pubmed=pubmed_id)

            # Check if other fields match
            # fields_match = all([
            #     biblio_entry.title == biblio_data["title"],
            #     biblio_entry.year == biblio_data["year"],
            # ])
            #
            # if not fields_match:
            #     # If they don't match, handle the mismatch. For now elet's not include this as existing entries may have different details than the ones we fetch from PubMed
            #     raise forms.ValidationError("A record with this PubMed ID already exists but with different details.")

        except DrugAgeBiblio.DoesNotExist:
            # If the entry doesn't exist, create a new one
            biblio_entry = DrugAgeBiblio.objects.create(
                pubmed_id=pubmed_id,
                title=biblio_data["title"],
                journal=biblio_data["journal"],
                year=biblio_data["year"],
                volume=biblio_data["volume"],
                issue=biblio_data["issue"],
                pages=biblio_data["pages"]
            )

        self.cleaned_data['BiblioId'] = biblio_entry
        return pubmed_id


