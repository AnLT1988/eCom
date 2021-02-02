from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name="pad")
@stringfilter
def pad(value, length):
    return value.zfill(length)
