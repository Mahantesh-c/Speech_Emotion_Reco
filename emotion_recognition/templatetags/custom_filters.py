from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """
    Split a string by a delimiter
    
    Usage: {{ value|split:"delimiter" }}
    """
    return value.split(arg)

@register.filter(name='mul')
def mul(value, arg):
    """
    Multiply a value by an argument
    
    Usage: {{ value|mul:100 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    
@register.filter(name='filter_by_source')
def filter_by_source(queryset, source_type):
    """
    Filter emotion results by source type (record or upload)
    
    Usage: {{ results|filter_by_source:"record" }}
    """
    return [item for item in queryset if item.audio_record.source == source_type]
@register.filter(name='get_item')
def get_item(container, key):
    """
    Get an item from a container (list, dictionary) by key
    
    Usage: {{ my_list|get_item:index }} or {{ my_dict|get_item:key }}
    """
    try:
        return container[key]
    except (KeyError, IndexError, TypeError):
        return None