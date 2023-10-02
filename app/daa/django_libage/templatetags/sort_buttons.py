from django import template

register = template.Library()

def sort_button(parser, token):
    try:
        tag_name, button_value, button_text, current_value = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("{0} tag requires three arguments".format(token.split_contents[0]))

    return SortButtonNode(button_value, button_text, current_value)

class SortButtonNode(template.Node):
    def __init__(self, button_value, button_text, current_value):
        self.button_value = button_value.strip('\'"')
        self.button_text = button_text.strip('\'"')
        self.current_value = template.Variable(current_value)

    def render(self, context):
        cv = self.current_value.resolve(context)
        styles = ''
        value = self.button_value
        text = self.button_text
        print cv
        if cv.strip('-') == self.button_value.strip('-'):
            styles = 'active'
            if cv.startswith('-'):
                value = self.button_value.strip('-')
                text = '-{}'.format(self.button_text.strip('-'))
            else:
                text = self.button_text.strip('-')
                value = '-{}'.format(self.button_value.strip('-'))
        return '<button type="submit" name="sort" class="btn {styles}" value="{value}">{text}</button>'.format(styles=styles, value=value, text=text)

register.tag('sort_button', sort_button)
