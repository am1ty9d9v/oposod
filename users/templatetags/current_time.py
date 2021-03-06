from django import template
import datetime
register = template.Library()

def current_time(parser, token ):
    try:
        tag_name, format_string = token.split_contents()
    except ValueError:
        msg = '%r requires a single argument' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
    return CurrentTimeNode(format_string[1:-1   ])


class CurrentTimeNode(template.Node):
    def __init__(self, format_string):
        self.format_string = str(format_string)

    def render(self, context):
        now = datetime.datetime.now()
        return now.strftime(self.format_string)

register.tag('current_time',  current_time)
