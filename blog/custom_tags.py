from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='dict_key_exists')
def dict_key_exists(dictionary, key):
    return key in dictionary