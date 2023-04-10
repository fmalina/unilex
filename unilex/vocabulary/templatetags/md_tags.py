from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.filter
def md(text):
    html = markdown.markdown(text)
    return mark_safe(html)
