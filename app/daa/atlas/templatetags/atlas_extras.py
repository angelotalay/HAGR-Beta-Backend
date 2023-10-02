import ast

from django.template import Library
register = Library()

@register.filter
def query_string(value, arg=""):
	qs = '?'
	value = value.copy()
	value.update(ast.literal_eval(arg))
	for name, item in value.iterlists():
		for v in item:
			qs += name+'='+v+'&'
	return qs.strip('&')

#register.filter('query_string', query_string)

@register.filter
def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return range( value )

@register.filter
def get_item(dictionary, key):
    """ Get an item for a dictionary with the provided key """
    return dictionary.get(key)
