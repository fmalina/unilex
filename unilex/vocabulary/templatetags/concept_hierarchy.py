from django import template

register = template.Library()


@register.filter
def multi(value, arg):
    return value * arg


@register.inclusion_tag('vocabulary/concept-list.html')
def render_concept_hierarchy(concept, depth=1, order=1):
    children = concept.get_children()
    return {'concept': concept, 'children': children,
            'depth': depth, 'order': order, 'render_children': bool(children)}
