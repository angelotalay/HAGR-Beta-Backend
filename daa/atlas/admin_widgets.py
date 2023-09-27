from django.contrib.admin.widgets import ForeignKeyRawIdWidget 
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext as _
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.forms.widgets import Input, TextInput 
from django.forms.utils import flatatt

from daa.atlas.models import *

class GenageDetailsLookupWidget(TextInput):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(self._format_value(value))
        lookup_button = u'<a class="btn button small lookup-widget" href="{0}" id="genage-human-lookup-details">Lookup details</a><span id="lookup-details-spinner" class="lookup-spinner spinner" style="display:none">Fetching...</span><span id="details-lookup-error" class="errornote inline-error" style="display: none"></span>'.format('/admin/genage_human/name/lookup/')
        #return mark_safe(u'<input%s />' % flatatt(final_attrs))
        input_field = u'<input%s />' % flatatt(final_attrs)
        return mark_safe(input_field+lookup_button)

class GeneLookupWidget(TextInput):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(self._format_value(value))
        lookup_button = u'<a class="btn button small lookup-widget" href="{0}" id="lookup-gene">Lookup Gene</a><span id="gene-lookup-spinner" class="spinner" style="display:none">Fetching...</span><span id="gene-lookup-error" class="errornote inline-error" style="display: none"></span>'.format('/admin/atlas/gene/lookup/')
        #return mark_safe(u'<input%s />' % flatatt(final_attrs))
        input_field = u'<input%s />' % flatatt(final_attrs)
        return mark_safe(input_field+lookup_button)

class ReferenceLookupWidget(TextInput):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        url = '../lookup/'
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(self._format_value(value))
        lookup_button = u'<a class="btn button small lookup-widget" href="{0}" id="lookup-reference">Lookup Reference</a><span id="reference-lookup-spinner" class="spinner" style="display:none">Fetching...</span><span id="reference-lookup-error" class="errornote inline-error" style="display: none"></span>'.format(url)#'/admin/atlas/reference/lookup/')
        #return mark_safe(u'<input%s />' % flatatt(final_attrs))
        input_field = u'<input%s />' % flatatt(final_attrs)
        return mark_safe(input_field+lookup_button)

class SelectableForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    
    def render(self, name, value, attrs=None):                                                                       
                                                                                                                     
        options = (('data', '---'), ('percentage', 'Percentage'), ('equation', 'Equation'), ('dataset', 'Dataset')) 
        
        selected = ''
        try:
            dt = Equation.objects.get(pk=value)
            selected = 'equation'
        except Equation.DoesNotExist:
            try:
                dt = Percentage.objects.get(pk=value)
                selected = 'percentage'
            except Percentage.DoesNotExist:
                try:
                    dt = Dataset.objects.get(pk=value)
                    selected = 'dataset'
                except:
                    selected = ''

        if attrs is None:
            attrs = {}                                                                                               
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, selected if selected != '' else self.rel.to._meta.object_name.lower())       
        params = self.url_parameters()
        if params: 
            url = u'?' + u'&amp;'.join([u'%s=%s' % (k, v) for k, v in params.items()])                               
        else:
            url = u''                                                                                                
        if "class" not in attrs:
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.                      
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)]                                     
        
        select_options = u''
        for o in options:
            is_selected = ''
            if o[0] == selected:
                is_selected = 'selected'
            if selected == '' and o[0] == 'data':
                is_selected = 'selected'
            select_options += u'<option value="%s" %s>%s</option>' % (o[0], is_selected, o[1], )
        selectbox = u'<select class="selectable-rawid-choices">%s</select>' % (select_options, )
        output.append(selectbox)                                                                         

        edit_url = '../../../%s/%s/%s' % (self.rel.to._meta.app_label, selected, value)
        
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically. 
        output.append(u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append(u'<img src="%simg/selector-search.gif" width="16" height="16" alt="%s" /></a>' % ('/static/admin/', _('Lookup')))
        if value:
            #output.append(self.label_for_value(value))                                                               
            output.append(u'&nbsp;&nbsp; <a href="%s%s" class="changelink edit-link" onclick="return showRelatedObjectLookupPopup(this);" title="Edit"> <i class="icon-pencil"></i> Edit</a>' % (edit_url, url+'&amp;_popup=1'))
        return mark_safe(u''.join(output))

class EditForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        edit_url = '../../../%s/%s/%s' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower(), value)
        params = self.url_parameters()
        if params:
            url = u'?' + u'&amp;'.join([u'%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = u''
        if "class" not in attrs:
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)]
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append(u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append(u'<img src="%simg/selector-search.gif" width="16" height="16" alt="%s" /></a>' % ('/static/admin/', _('Lookup')))
        if value:
            output.append(self.label_for_value(value))
            output.append(u'&nbsp;&nbsp; <a href="%s%s" class="changelink edit-link" onclick="return showRelatedObjectLookupPopup(this);" title="Edit"> <i class="icon-pencil"></i> Edit</a>' % (edit_url, url+'&amp;_popup=1'))
        return mark_safe(u''.join(output))

class DataForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}

        button_list = ['percentage', 'equation', 'dataset']

        # Get type of data
        current_type = None
        if value:
            data = Data.objects.get(id=value)
            if hasattr(data, 'percentage'):
                current_type = 'percentage'
                button_list.insert(0, button_list.pop(0))
            elif hasattr(data, 'equation'):
                current_type = 'equation'
                button_list.insert(0, button_list.pop(1))
            elif hasattr(data, 'dataset'):
                current_type = 'dataset'
                button_list.insert(0, button_list.pop(2))

        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        edit_url = '../../../%s/%s/%s' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower(), value)
        params = self.url_parameters()
        if params:
            url = u'?' + u'&amp;'.join([u'%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = u''
        if "class" not in attrs:
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)]
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        #output.append(u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % (related_url, url, name))
        #output.append(u'<img src="%simg/selector-search.gif" width="16" height="16" alt="%s" /></a>' % ('/static/admin/', _('Lookup')))
            #output.append(u' <a href="%s%s" class="changelink edit-link" onclick="return showRelatedObjectLookupPopup(this);" title="Edit"></a>' % (edit_url, url+'&amp;_popup=1'))
        #if value:
        #    output.append(self.label_for_value(value))
        output.append(u'<div class="btn-group">')
        for i,b in enumerate(button_list):
            if i == 0:
                pclass = '' if value else 'left'
            elif i == 1:
                pclass = 'left' if value else 'middle'
            else:
                pclass = 'right'
            status = 'add'
            label = 'Add {0}'.format(b)
            if value:
                label = 'Change to {0}'.format(b)
            querystring = '/add/?_popup=1'
            if b == current_type:
                status = 'edit'
                pclass = 'blue-button btn-info'
                label = 'Edit {0}'.format(b)
                querystring = '/{0}?t=id&amp;_popup=1'.format(value)
            output.append(u'<a id="lookup_id_{name}" href="../../../atlas/{type}{q}" onclick="return showRelatedObjectLookupPopup(this);" class="btn button {position_class}">{label}</a>'.format(type=b, status=status, position_class=pclass, label=label, q=querystring, name=name))
        output.append(u'</div>')
        return mark_safe(u''.join(output))
        
class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        if value and self.max_choices and len(value) > self.max_choices:
            raise forms.ValidationError('You must select a maximum of %s choice%s.'
                    % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value

class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)
        
    def validate(self, value, model_instance): 
        return

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name), 
                    'help_text': self.help_text, 'choices':self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        elif value is None:
            return ''
        return value.split(",")

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices):",".join([choicedict.get(value,value) for value in getattr(self,fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)
