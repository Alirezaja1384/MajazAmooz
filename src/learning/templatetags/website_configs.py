# TODO: Make configurations dynamic
from django import template


register = template.Library()


@register.simple_tag
def website_description():
    description = ('با هم مجازی می آموزیم! '
                   'مجاز آموز، جامعه ای از دانش آموزان سراسر ایران است که '
                   'با استفاده از فضای آنلاین در هر مکان و زمان به آموزش دسترسی دارند '
                   'و به یکدیگر آموزش می دهند.')
    return description


@register.simple_tag
def website_keywords():
    keywords = ['آموزش', 'درسنامه', 'آزمون', 'آموزش مجازی', 'آزمون آنلاین']
    return ', '.join(keywords)
