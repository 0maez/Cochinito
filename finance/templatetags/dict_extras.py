# finance/templatetags/dict_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Devuelve el valor de la clave en el diccionario."""
    return dictionary.get(key)
