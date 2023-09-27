from django import forms
from daa.atlas.admin_widgets import ReferenceLookupWidget

class ReferenceAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'pubmed': ReferenceLookupWidget,
        }

