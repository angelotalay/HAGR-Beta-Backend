import json
import urllib2

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()

def reference(parser, token):
    try:
        tag_name, identifier = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("{0} tag requires one argument".format(token.split_contents[0]))
    return ReferenceNode(identifier)

class ReferenceNode(template.Node):
    def __init__(self, identifier):
        self.identifier = template.Variable(identifier)

    def render(self, context):
        id = self.identifier.resolve(context)
        url = '{0}/get/{1}/{2}/'.format(settings.LIBAGE_ENDPOINT, settings.LIBAGE_DATABASE, id)
        try:
            response = urllib2.urlopen(url).read()
        except:
            response = '{}'
        results = json.loads(response)

        refs = ''
        for r in results:
            refs += u'<li><span class="libage-reference">{0}</span><div class="libage-link-container"><a href="{1}" class="libage-reference-details-link">Other changes</a><a href="{2}" class="libage-entry-link">View LibAge entry</a></div></li>'.format(r['reference'], reverse('libage:entry', args=(r['id'],)), settings.LIBAGE_URL+r['url'])
        html = u'<ul class="libage-reference-list">{0}</ul><a href="{1}" class="libage-link">Referencing provided by LibAge</a>'.format(refs, settings.LIBAGE_URL)

        return html

register.tag('references', reference)
