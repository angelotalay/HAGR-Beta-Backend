from django import forms
from django.forms.widgets import Widget, Input, TextInput, SelectMultiple
from django.utils.encoding import force_unicode
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.conf import settings
from django.core.urlresolvers import reverse

from daa.django_libage.models import Citation

class LibageReferencesWidget(SelectMultiple):
    def __init__(self, extra_attrs=None, *args, **kwargs):
        super(LibageReferencesWidget, self).__init__(*args, **kwargs)
        self.extra_attrs = extra_attrs

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {} 

        output = []
        existing = []

        errors = ''

        if value is not None and len(value) > 0:
            if 'database' not in self.extra_attrs:
                self.extra_attrs['database'] = 'daa'
            try:
                cite = Citation.objects.get(identifier=value[0], source__short_name=self.extra_attrs['database'])
                url = reverse('admin:django_libage_citation_change', args=(cite.id,))
                text = u'Edit References'
                for r in cite.bibliographicentry_set.all():
                    existing.append(u'<li><b>[{0}]:</b> {1}</li>'.format(r.id, r.formatted_reference()))
            except Citation.DoesNotExist:
                url = reverse('admin:django_libage_citation_add')
                text = u'Add References'
            except Citation.MultipleObjectsReturned:
                cite = Citation.objects.filter(identifier=value[0])[0]
                errors = u'This change has MULTIPLE citations. Please use the LibAge interface to correct this.'
                url = reverse('admin:django_libage_citation_change', args=(cite.id,))
                text = u'Edit References'
                for r in cite.bibliographicentry_set.all():
                    existing.append(u'<li>{0}</li>'.format(r.formatted_reference()))
        else:
            url = reverse('admin:django_libage_citation_add')
            text = u'Add References'

        identifier_name = u'id_'+name.replace('libage_references', 'identifier')

        if len(existing) > 0:
            output.append(u'<ul id="{0}_reflist">{1}</ul>'.format(name, u"".join(existing)))
        else:
            output.append(u'<ul id="{0}_reflist"></ul>'.format(name))

        name_fields = u'[{}]'.format(u",".join([u"'"+unicode(nf)+u"'" for nf in self.extra_attrs['name_fields']]))
        output.append(u'<p>{errors}</p><p><a href="{url}?{param}" class="button related-lookup" id="{widget_id}" onclick="return showLibageReferencePopup(this, \'{identifier_name}\', {name_fields}, {source_id});">{text}</a></p>'.format(url=url, param='_popup=1', text=text, errors=errors, name_fields=name_fields, source_id=self.extra_attrs['source_id'], widget_id=name, identifier_name=identifier_name))

        return mark_safe(u''.join(output))

class LibageReferencesField(forms.MultipleChoiceField):
    def __init__(self, required=True, label=None, initial=None, widget=None, help_text='', attrs={'name_fields': ['id_name'], 'source_id': 4}, *args, **kwargs):
        self.widget = LibageReferencesWidget(extra_attrs=attrs, *args, **kwargs)
        super(LibageReferencesField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return value

