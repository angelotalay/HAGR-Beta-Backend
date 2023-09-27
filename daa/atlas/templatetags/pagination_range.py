from django.template import Library, Variable, Node
register = Library()

#from django_tables2 import querystring

class PaginationRangeNode(Node):

	def __init__(self, start, end):
		self.start = start
		self.end = end
	
	def render(self, context):
		start = self.start.resolve(context)
		end = self.end.resolve(context)
		pages_from = 1 if (start-5) < 1 else start - 4
		pages_to = end if (start+5) > end else start + 5 
		page_range = range(pages_from, pages_to)

		context['pagination_range'] = page_range
		return ''
		

@register.tag
def pagination_range(parser, token):
	"""
	Accepts two inputs: the current page and total number of pages

	Syntax:
		{% pagination_range start stop %}

	Produces:
		<ul>
			<li><a href="
	"""
	tag_name, start_var, end_var = token.split_contents()
	start = Variable(start_var)
	end = Variable(end_var)
	return PaginationRangeNode(start, end)
