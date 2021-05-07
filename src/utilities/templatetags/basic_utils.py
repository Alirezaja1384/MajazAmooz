"""
    Basic template-tags
"""
from django import template

register = template.Library()

@register.filter
def page_range(page_count: int):
    return range(1, page_count + 1)
