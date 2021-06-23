from django import template
from constance import config

register = template.Library()


@register.simple_tag
def website_description():
    return config.WEBSITE_DESCRIPTION


@register.simple_tag
def website_keywords():
    return config.WEBSITE_KEYWORDS
