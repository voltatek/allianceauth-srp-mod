import random
from django import template
register = template.Library()

@register.simple_tag
def random_colour():
    r = lambda: random.randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())
